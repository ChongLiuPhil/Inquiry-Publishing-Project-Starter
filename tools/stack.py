#!/usr/bin/env python3
import argparse
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]

def load(path):
    p = ROOT / path
    if not p.is_file():
        raise SystemExit(f"ERROR: missing {path}")
    return yaml.safe_load(p.read_text(encoding="utf-8"))

def check():
    stack = load("project-stack.yaml")
    lock = load("project-stack.lock.yaml")
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

def main():
    p = argparse.ArgumentParser()
    p.add_argument("command", choices=["check","doctor"])
    args = p.parse_args()
    {"check": check, "doctor": doctor}[args.command]()

if __name__ == "__main__":
    main()
