#!/usr/bin/env python3
"""Reconcile registered public outputs after a commit event or manual recovery.

Compare fixed source files or complete rendered deliverables without credentials.
The workflow validates the candidate before committing the changed lock.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from build_public_site import MANIFEST, REPOSITORIES, validate_lock

ROOT = Path(__file__).resolve().parents[1]
LOCK_PATH = ROOT / "site" / "sources.lock.json"
API = "https://api.github.com/repos"
RAW = "https://raw.githubusercontent.com"


def get_bytes(url: str) -> bytes:
    request = Request(url, headers={"User-Agent": "inquiry-publishing-stack-source-sync", "Accept": "application/vnd.github+json"})
    with urlopen(request, timeout=30) as response:
        return response.read()


def latest_revision(repository: str) -> str:
    payload = json.loads(get_bytes(f"{API}/{repository}/commits?per_page=1"))
    if not payload or not re.fullmatch(r"[0-9a-f]{40}", payload[0].get("sha", "")):
        raise RuntimeError(f"Could not resolve the public default-branch revision for {repository}")
    return payload[0]["sha"]


def resolve_event(repository: str, branch: str, revision: str, get=get_bytes) -> str:
    """Treat notifications as hints; never trust caller-supplied content or URLs."""
    configs = {v["repository"]: v for k, v in {**MANIFEST["components"], **MANIFEST.get("publications", {})}.items() if k != "starter"}
    if repository not in configs or branch != configs[repository]["branch"]:
        raise ValueError("Unregistered repository or publication branch")
    if not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ValueError("Notification must contain a full commit SHA")
    metadata = json.loads(get(f"{API}/{repository}"))
    if metadata.get("private") is not False or metadata.get("default_branch") != branch:
        raise ValueError("Source is not public or its default branch has drifted")
    head = json.loads(get(f"{API}/{repository}/commits/{branch}"))["sha"]
    if not re.fullmatch(r"[0-9a-f]{40}", head):
        raise ValueError("Invalid default-branch head")
    if revision != head:
        comparison = json.loads(get(f"{API}/{repository}/compare/{revision}...{head}"))
        if comparison.get("status") not in ("ahead", "identical"):
            raise ValueError("Notification is not on the publication branch")
    return head  # Coalesce delayed events onto current head, never roll back.


def source_bytes(repository: str, revision: str, path: str) -> bytes:
    try:
        return get_bytes(f"{RAW}/{repository}/{revision}/{path}")
    except HTTPError as exc:
        raise RuntimeError(f"Could not read allowlisted public source {repository}@{revision}:{path} ({exc.code})") from exc


def refresh(lock_path: Path = LOCK_PATH, *, apply: bool = False, resolve=latest_revision, read_file=source_bytes, repository: str | None = None) -> list[str]:
    original = lock_path.read_text(encoding="utf-8")
    lock = json.loads(original)
    validate_lock(lock)
    replacements: list[tuple[str, str, str]] = []

    for key, component in lock["components"].items():
        if key == "starter" or (repository and component["repository"] != repository):
            continue
        source_repository = REPOSITORIES[key]
        old_revision = component["revision"]
        new_revision = resolve(source_repository)
        if new_revision == old_revision:
            continue
        changed = any(
            hashlib.sha256(read_file(source_repository, old_revision, path)).digest()
            != hashlib.sha256(read_file(source_repository, new_revision, path)).digest()
            for path in component["files"]
        )
        if changed:
            replacements.append((key, old_revision, new_revision))

    from publication_outputs import build_remote, digest
    for key, spec in MANIFEST.get('publications', {}).items():
        if repository and spec['repository'] != repository:
            continue
        old_revision = lock['publications'][key]['revision']
        new_revision = resolve(spec['repository'])
        if old_revision != new_revision and digest(build_remote(spec, old_revision)) != digest(build_remote(spec, new_revision)):
            replacements.append((key, old_revision, new_revision))

    if not replacements:
        print("Registered publication output is unchanged; no source lock commit required.")
        return []

    updated = original
    for key, old_revision, new_revision in replacements:
        old = f'"revision": "{old_revision}"'
        new = f'"revision": "{new_revision}"'
        if updated.count(old) != 1:
            raise RuntimeError(f"Expected one unique lock entry for {key}; refusing ambiguous update")
        updated = updated.replace(old, new, 1)
        print(f"Public content changed: {key} -> {new_revision}")

    if apply:
        updated_lock = json.loads(updated)
        validate_lock(updated_lock)
        temporary = lock_path.with_suffix(lock_path.suffix + ".tmp")
        temporary.write_text(updated, encoding="utf-8")
        temporary.replace(lock_path)
    else:
        print("Dry run only; pass --apply to update site/sources.lock.json.")

    output_path = os.environ.get("GITHUB_OUTPUT")
    if apply and output_path:
        with open(output_path, "a", encoding="utf-8") as output:
            output.write("changed=true\n")
    return [key for key, _, _ in replacements]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true", help="write changed public source revisions to the lock")
    parser.add_argument("--repository", default=os.environ.get("SOURCE_REPOSITORY", ""))
    parser.add_argument("--branch", default=os.environ.get("SOURCE_BRANCH", ""))
    parser.add_argument("--revision", default=os.environ.get("SOURCE_REVISION", ""))
    args = parser.parse_args()
    supplied = (args.repository, args.branch, args.revision)
    if any(supplied) and not all(supplied):
        raise ValueError("Supply repository, branch and revision together")
    if all(supplied):
        resolve_event(*supplied)
    # Every event converges all sources. GitHub concurrency may replace a pending
    # run; a later event must also recover earlier notifications from other repos.
    def resolve(repository):
        branch = next(v["branch"] for v in {**MANIFEST["components"], **MANIFEST.get("publications", {})}.values() if v["repository"] == repository)
        return resolve_event(repository, branch, latest_revision(repository))
    refresh(apply=args.apply, resolve=resolve)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
