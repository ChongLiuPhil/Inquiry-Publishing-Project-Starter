"""Build complete, explicitly registered public deliverables without credentials."""
from __future__ import annotations
import hashlib
import io
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import tarfile
import tempfile
from urllib.request import Request, urlopen

MAX_FILE = 25 * 1024 * 1024
MAX_TOTAL = 200 * 1024 * 1024


def relative(value: str) -> str:
    path = PurePosixPath(value)
    if not value or path.is_absolute() or '..' in path.parts or '\\' in value or str(path) != value:
        raise ValueError('Expected a normalized relative publication path')
    return value


def validate_spec(spec: dict) -> None:
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', spec.get('repository', '')):
        raise ValueError('Invalid publication repository')
    if spec.get('visibility') != 'public':
        raise ValueError('Only explicitly public outputs may join this public site')
    if spec.get('build', {}).get('kind') not in ('static-directory', 'quarto'):
        raise ValueError('Unsupported publication build')
    relative(spec['output_directory'])
    relative(spec.get('source_directory', '.'))
    mount = spec.get('mount', '')
    if not re.fullmatch(r'/publications/[a-z0-9][a-z0-9-]*/', mount):
        raise ValueError('Publications require a distinct /publications/<name>/ mount')
    if spec['build']['kind'] == 'quarto' and not re.fullmatch(r'\d+\.\d+\.\d+', spec['build'].get('version', '')):
        raise ValueError('Pin the Quarto runtime version')


def snapshot(directory: Path) -> dict[str, bytes]:
    if not directory.is_dir() or directory.is_symlink():
        raise ValueError('Missing or linked publication output directory')
    files = {}
    total = 0
    for path in sorted(directory.rglob('*')):
        if path.is_symlink():
            raise ValueError('Symlinks are not publication assets')
        if not path.is_file():
            continue
        rel = path.relative_to(directory).as_posix()
        if any(part.startswith('.') for part in PurePosixPath(rel).parts):
            raise ValueError('Hidden files are not publication assets')
        size = path.stat().st_size
        total += size
        if size > MAX_FILE or total > MAX_TOTAL:
            raise ValueError('Publication exceeds the configured size budget')
        files[rel] = path.read_bytes()
    if 'index.html' not in files:
        raise ValueError('Publication needs index.html')
    return files


def build_local(checkout: Path, spec: dict) -> dict[str, bytes]:
    validate_spec(spec)
    source = checkout / spec.get('source_directory', '.')
    output = checkout / spec['output_directory']
    for path in (source, output):
        if not path.resolve().is_relative_to(checkout.resolve()):
            raise ValueError('Publication path escapes checkout')
    if spec['build']['kind'] == 'quarto':
        if source.resolve().is_relative_to(output.resolve()):
            raise ValueError('Generated output must not contain source directory')
        if output.is_symlink():
            raise ValueError('Linked output directory')
        if output.exists():
            shutil.rmtree(output)
        # Never inherit API tokens, runner credentials, Git config or user HOME.
        with tempfile.TemporaryDirectory(prefix='publication-home-') as home:
            env = {'PATH': os.defpath + os.pathsep + os.environ.get('PATH', ''), 'HOME': home,
                   'LANG': 'C.UTF-8', 'TZ': 'UTC'}
            version = subprocess.check_output(['quarto', '--version'], env=env, text=True).strip()
            if version != spec['build']['version']:
                raise ValueError('Installed Quarto version does not match publication manifest')
            result = subprocess.run(['quarto', 'render', '.', '--to', 'html', '--output-dir', str(output.resolve())],
                                    cwd=source, env=env, capture_output=True, timeout=600)
            if result.returncode:
                # Source-controlled build output can contain arbitrary text. Do not echo it.
                raise ValueError('Quarto publication build failed')
    return snapshot(output)


def build_remote(spec: dict, revision: str) -> dict[str, bytes]:
    validate_spec(spec)
    if not re.fullmatch(r'[0-9a-f]{40}', revision):
        raise ValueError('Publication revision must be immutable')
    url = f'https://codeload.github.com/{spec["repository"]}/tar.gz/{revision}'
    with urlopen(Request(url, headers={'User-Agent': 'Inquiry-Publishing-Stack'}), timeout=60) as response:
        data = response.read(MAX_TOTAL + 1)
    if len(data) > MAX_TOTAL:
        raise ValueError('Source archive exceeds size budget')
    with tempfile.TemporaryDirectory(prefix='publication-source-') as tmp:
        checkout = Path(tmp)
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as archive:
            total = 0
            for member in archive:
                parts = PurePosixPath(member.name).parts
                if len(parts) < 2:
                    continue
                rel = '/'.join(parts[1:])
                relative(rel)
                if not (member.isfile() or member.isdir()):
                    raise ValueError('Source archive contains links or special files')
                total += member.size
                if member.size > MAX_FILE or total > MAX_TOTAL:
                    raise ValueError('Expanded source exceeds size budget')
                target = checkout / rel
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                else:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with archive.extractfile(member) as source:
                        target.write_bytes(source.read())
        return build_local(checkout, spec)


def digest(files: dict[str, bytes]) -> dict[str, str]:
    return {path: hashlib.sha256(data).hexdigest() for path, data in sorted(files.items())}
