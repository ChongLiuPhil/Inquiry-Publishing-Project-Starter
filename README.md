# Inquiry Publishing Project Starter

[中文](README.zh-CN.md)

This repository is the **composition, adoption, and upgrade layer** for three independent upstream systems:

- [AI-Assisted Human Inquiry and Creation Protocol (AHICP)](https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol) — human-led, AI-assisted inquiry and creation governance;
- [Personal Publishing Framework (PPF)](https://github.com/ChongLiuPhil/Personal-Publishing-Framework) — source/build/publish/release/archive lifecycle;
- [Vault Interface](https://github.com/ChongLiuPhil/Vault-interface) — public, portable `project.yaml` and `website.yaml` metadata contracts.

The Starter is **not a fourth normative framework**. The upstream repositories remain authoritative.

## Profiles

- `research-only`
- `publishing-only`
- `research-book`
- `full-research-publication`

A profile describes composition complexity, not project value.

## Machine-readable adoption

Run:

```bash
python -m pip install -r requirements-validation.txt
make stack-check
make adoption-plan
```

For machine-oriented output:

```bash
python tools/stack.py adoption-plan --json
```

The plan reports each component's authoritative repository, pinned revision, template root/manifest, and the file-ownership policy.

## Upgrade safety

`stack/managed-paths.yaml` separates:

- **upstream-managed** paths that may be updated from a pinned upstream revision;
- **merge-managed** paths that require a base/current/new three-way comparison;
- **project-owned** paths that must never be overwritten automatically.

Existing reliable project files should be functionally mapped before creating duplicate sources of truth. Human approvals, research decisions, publication authorization, canonical identity, and provider actual state are preserved unless the human explicitly changes them.

## Durable provenance

`project-stack.yaml` declares adopted upstream revisions. `project-stack.lock.yaml` freezes the resolved stack after adoption. Run `python tools/freeze_stack_lock.py` after the project is initialized or upgraded.

See [AI adoption and upgrade workflow](docs/AI_ADOPTION_WORKFLOW.md).
