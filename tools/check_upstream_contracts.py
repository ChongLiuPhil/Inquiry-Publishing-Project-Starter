#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import urllib.request
import yaml

ROOT = Path(__file__).resolve().parents[1]
ROLE_TO_SOURCE = {
    "governance": "ahicp",
    "publishing": "ppf",
    "portfolio_interface": "vault-interface",
}

def load(root, path):
    p = root / path
    if not p.is_file():
        raise SystemExit(f"ERROR: missing {p}")
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def fetch_yaml(repository, revision, path):
    url = f"https://raw.githubusercontent.com/{repository}/{revision}/{path}"
    req = urllib.request.Request(url, headers={"User-Agent":"inquiry-publishing-stack-upstream-check"})
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return yaml.safe_load(response.read().decode("utf-8"))
    except Exception as e:
        raise SystemExit(f"ERROR: cannot fetch {repository}@{revision}:{path}: {e}")

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--root", default=str(ROOT))
    args=p.parse_args()
    root=Path(args.root).resolve()

    stack=load(root,"project-stack.yaml")
    source_map=load(root,"stack/source-map.yaml")["sources"]
    errors=[]

    for role, source_key in ROLE_TO_SOURCE.items():
        component=stack.get("components",{}).get(role)
        if not component or component.get("adoption_state") != "active":
            continue
        src=source_map[source_key]
        if component.get("source") != src.get("repository"):
            errors.append(f"{role}: component source differs from source-map")
            continue
        revision=component.get("template_source_commit")
        manifest=fetch_yaml(component["source"], revision, src["manifest_path"])

        if manifest.get("template_root") and manifest.get("template_root") != src.get("template_root"):
            errors.append(f"{role}: upstream template_root differs from source-map")

        if role == "governance":
            profile=component.get("profile")
            if profile and profile != "legacy-functional-mapping" and profile not in (manifest.get("profiles") or {}):
                errors.append(f"governance profile not declared by pinned AHICP manifest: {profile}")
        elif role == "publishing":
            profile=component.get("profile")
            declared=manifest.get("profile")
            if profile and declared != profile:
                errors.append(f"publishing profile {profile!r} != pinned PPF manifest profile {declared!r}")
        elif role == "portfolio_interface":
            version=component.get("version")
            declared=manifest.get("version")
            if version and declared != version:
                errors.append(f"Vault Interface version {version!r} != pinned manifest version {declared!r}")

        print(f"OK {role}: {component['source']}@{revision} -> {src['manifest_path']}")

    if errors:
        for e in errors:
            print("ERROR:",e,file=sys.stderr)
        raise SystemExit(1)
    print("Pinned upstream contracts are compatible with the declared stack.")

if __name__ == "__main__":
    main()
