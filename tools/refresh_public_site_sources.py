#!/usr/bin/env python3
"""Refresh the public-site source lock when allowlisted public files change.

This intentionally reads only the pinned source files and their public default
branches. It has no credentials and never copies files into the repository.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from build_public_site import REPOSITORIES, validate_lock

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


def source_bytes(repository: str, revision: str, path: str) -> bytes:
    try:
        return get_bytes(f"{RAW}/{repository}/{revision}/{path}")
    except HTTPError as exc:
        raise RuntimeError(f"Could not read allowlisted public source {repository}@{revision}:{path} ({exc.code})") from exc


def refresh(lock_path: Path = LOCK_PATH, *, apply: bool = False, resolve=latest_revision, read_file=source_bytes) -> list[str]:
    original = lock_path.read_text(encoding="utf-8")
    lock = json.loads(original)
    validate_lock(lock)
    replacements: list[tuple[str, str, str]] = []

    for key, component in lock["components"].items():
        if key == "starter":
            continue
        repository = REPOSITORIES[key]
        old_revision = component["revision"]
        new_revision = resolve(repository)
        if new_revision == old_revision:
            continue
        changed = any(
            hashlib.sha256(read_file(repository, old_revision, path)).digest()
            != hashlib.sha256(read_file(repository, new_revision, path)).digest()
            for path in component["files"]
        )
        if changed:
            replacements.append((key, old_revision, new_revision))

    if not replacements:
        print("Public allowlisted content is unchanged; source lock remains current.")
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
    args = parser.parse_args()
    refresh(apply=args.apply)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
