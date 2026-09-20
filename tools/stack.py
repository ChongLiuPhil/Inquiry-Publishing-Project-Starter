#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import sys
import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    p = ROOT / path
    if not p.is_file():
        raise SystemExit(f"ERROR: missing {path}")
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def load_json(path):
    p = ROOT / path
    if not p.is_file():
        raise SystemExit(f"ERROR: missing {path}")
    return json.loads(p.read_text(encoding="utf-8"))

def validate_schema(instance, schema_path, label):
    validator = Draft202012Validator(load_json(schema_path))
    errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.path))
    if errors:
        for e in errors:
            where = ".".join(str(x) for x in e.path) or "<root>"
            print(f"ERROR {label} {where}: {e.message}", file=sys.stderr)
        raise SystemExit(1)

def check():
    stack = load("project-stack.yaml")
    lock = load("project-stack.lock.yaml")
    validate_schema(stack, "schema/project-stack.schema.json", "project-stack")
    validate_schema(lock, "schema/project-stack-lock.schema.json", "project-stack.lock")
    errors = []

    expected = stack.get("components", {})
    resolved = lock.get("resolved", {})
    for key, lock_key in (("governance","ahicp"),("publishing","ppf"),("portfolio_interface","vault_interface")):
        commit = expected.get(key, {}).get("adopted_commit")
        if commit and resolved.get(lock_key) != commit:
            errors.append(f"lock drift: {lock_key} != {commit}")

    template_project = load("templates/project.yaml")
    template_website = load("templates/website.yaml")
    template_publishing = load("templates/publishing.yaml")
    pid = stack.get("project", {}).get("id")
    for label, value in (
        ("templates/project.yaml", template_project.get("id")),
        ("templates/website.yaml", template_website.get("project_id")),
        ("templates/publishing.yaml", template_publishing.get("project", {}).get("id")),
    ):
        if value != pid:
            errors.append(f"{label} project id {value!r} != stack id {pid!r}")

    web = template_publishing.get("publication", {}).get("web", {})
    dep = template_publishing.get("deployment", {}).get("web", {})
    if web.get("authorization_state") != "authorized" and dep.get("enabled") is True:
        errors.append("deployment cannot be enabled before publication authorization")
    if template_website.get("publish") is True and web.get("authorization_state") != "authorized":
        errors.append("website.publish=true requires PPF Web authorization")

    source_map = load("stack/source-map.yaml")
    declared = set(source_map.get("sources", {}))
    for key in ("governance","publishing","portfolio_interface"):
        source_key = expected.get(key, {}).get("framework")
        if source_key and source_key not in declared:
            errors.append(f"source-map missing framework: {source_key}")

    profile = stack.get("profile")
    profile_path = ROOT / "profiles" / f"{profile}.yaml"
    if not profile_path.is_file():
        errors.append(f"missing profile definition: profiles/{profile}.yaml")

    if errors:
        for e in errors:
            print("ERROR:", e, file=sys.stderr)
        raise SystemExit(1)
    print("Stack consistency check passed.")

def doctor():
    stack = load("project-stack.yaml")
    print("profile:", stack.get("profile"))
    for name, data in stack.get("components", {}).items():
        print(f"{name}: {data.get('source')} @ {data.get('adopted_commit')}")
    try:
        check()
    except SystemExit:
        print("stack health: DRIFTED")
        raise
    print("stack health: CONSISTENT")

def build_adoption_plan():
    stack = load("project-stack.yaml")
    source_map = load("stack/source-map.yaml")
    managed = load("stack/managed-paths.yaml")
    profile = load(f"profiles/{stack['profile']}.yaml")
    plan = {
        "schema": "inquiry-publishing-adoption-plan/v1",
        "project_id": stack["project"]["id"],
        "profile": stack["profile"],
        "components": [],
        "ownership": {
            "upstream_managed": managed.get("upstream_managed", []),
            "merge_managed": managed.get("merge_managed", []),
            "project_owned": managed.get("project_owned", []),
        },
        "rules": [
            "fresh-read each upstream revision before write",
            "never overwrite project-owned paths automatically",
            "three-way compare merge-managed paths",
            "preserve human approvals and provider actual state",
            "apply through branch/PR and run project-local gates",
        ],
    }
    components = stack["components"]
    role_to_key = {
        "governance": "ahicp",
        "publishing": "ppf",
        "portfolio_interface": "vault-interface",
    }
    requested = set(profile.get("components", []))
    for role, source_key in role_to_key.items():
        data = components.get(role)
        if not data or source_key not in requested:
            continue
        src = source_map["sources"][source_key]
        plan["components"].append({
            "role": role,
            "framework": data.get("framework"),
            "repository": data.get("source"),
            "revision": data.get("adopted_commit"),
            "template_root": src.get("template_root"),
            "manifest_path": src.get("manifest_path"),
            "adoption_mode": src.get("adoption_mode"),
        })
    return plan

def adoption_plan(as_json=False):
    plan = build_adoption_plan()
    if as_json:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return
    print(f"project: {plan['project_id']}")
    print(f"profile: {plan['profile']}")
    for c in plan["components"]:
        print(f"- {c['role']}: {c['repository']} @ {c['revision']}")
        print(f"  template_root: {c['template_root']}")
        print(f"  manifest_path: {c['manifest_path']}")
        print(f"  adoption_mode: {c['adoption_mode']}")
    print("ownership policy: stack/managed-paths.yaml")
    print("rule: project-owned paths are never overwritten automatically")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["check","doctor","adoption-plan"])
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    if args.command == "check":
        check()
    elif args.command == "doctor":
        doctor()
    else:
        adoption_plan(args.json)

if __name__ == "__main__":
    main()
