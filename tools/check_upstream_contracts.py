#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
from pathlib import Path
import sys
import urllib.request
import yaml
from jsonschema import Draft202012Validator

from project_provisioning import build_plan

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

            provisioning_path = root / "project-provisioning.yaml"
            if provisioning_path.is_file():
                request = load(root, "project-provisioning.yaml")
                platform = copy.deepcopy(load(ROOT, "templates/platform-authorization.yaml"))
                owner_type = request.get("infrastructure", {}).get("github", {}).get("owner_type")
                owner = request.get("infrastructure", {}).get("github", {}).get("owner")
                platform["status"] = "ready"
                platform["github"].update({
                    "owner_scope": owner,
                    "principal_ref": "ci-synthetic-github-principal",
                    "principal_type": "github-app-user-access" if owner_type == "user" else "github-app-installation",
                    "authorization_state": "authorized",
                })
                platform["cloudflare"].update({
                    "account_ref": "ci-synthetic-cloudflare-account",
                    "principal_ref": "ci-synthetic-cloudflare-principal",
                    "authorization_state": "authorized",
                    "all_workers_access": "verified",
                    "worker_creation_authority": "authorized",
                })
                platform["secret_broker"].update({
                    "implementation_ref": "ci-synthetic-secret-broker",
                    "state": "verified",
                    "plaintext_boundary": "verified",
                    "token_minting_authority": "isolated-authorized",
                })
                platform["standing_authorizations"].update({
                    "create_private_repositories": True,
                    "create_restricted_workers": True,
                    "restricted_web_deployment": True,
                })
                plan = build_plan(platform, request)
                if plan.get("status") != "READY_FOR_PROVISIONER":
                    errors.append("Starter provisioning plan is not ready under a synthetic verified platform baseline")
                else:
                    schema = fetch_yaml(component["source"], revision, "schema/project.infrastructure.schema.json")
                    desired = plan["ppf_handoff"]["desired_state_seed"]
                    schema_errors = sorted(
                        Draft202012Validator(schema).iter_errors(desired),
                        key=lambda error: list(error.path),
                    )
                    if schema_errors:
                        first = schema_errors[0]
                        where = ".".join(str(part) for part in first.path) or "<root>"
                        errors.append(f"Starter PPF desired-state seed violates pinned PPF schema at {where}: {first.message}")
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
