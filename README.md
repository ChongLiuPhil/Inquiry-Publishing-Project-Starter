# Inquiry Publishing Project Starter

[中文](README.zh-CN.md)

This repository is the **composition, adoption, and upgrade layer** for three independent upstream systems:

- [AI-Assisted Human Inquiry and Creation Protocol (AHICP)](https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol)
- [Personal Publishing Framework (PPF)](https://github.com/ChongLiuPhil/Personal-Publishing-Framework)
- [Vault Interface](https://github.com/ChongLiuPhil/Vault-interface)

The Starter is **not a fourth normative framework**. Upstream repositories remain authoritative.

## Stack v2

Stack v2 distinguishes three facts that must not be collapsed:

- `template_source_commit`: the pinned upstream template/manifest revision used for composition and upgrade mechanics;
- `project_adopted_commit`: the semantic framework revision actually adopted by the project, when applicable;
- `adoption_state`: `active`, `deferred`, or `not-applicable`.

This allows legacy functional mapping and optional/deferred publication without inventing adoption history.

## Profiles

- `research-only`: Vault Interface + AHICP
- `publishing-only`: Vault Interface + PPF
- `research-book`: Vault Interface + AHICP, with PPF optional
- `full-research-publication`: all three active

A profile describes composition, not project value.

## Machine-readable adoption

```bash
python -m pip install -r requirements-validation.txt
make stack-check
make stack-test
make upstream-check
make adoption-plan
```

For machine-oriented output:

```bash
python tools/stack.py adoption-plan --json
```

The adoption plan reports active/deferred component state, authoritative repository, pinned template revision, and the exact upstream manifest that owns upgrade classification.

## Upgrade safety

Starter does **not** copy AHICP or PPF ownership lists. For each active component, an agent must fresh-read the component manifest at its pinned `template_source_commit`. That upstream manifest is authoritative for `upstream-managed`, `merge-managed`, and `project-owned` paths.

Existing reliable files should be functionally mapped before duplicate truth sources are created. Human approvals, research decisions, publication authorization, canonical identity, and provider actual state are preserved unless the human explicitly changes them.

## Durable provenance

`project-stack.yaml` declares component state and source revisions. `project-stack.lock.yaml` freezes resolved template revisions.

Before freezing a generated project, replace `starter.adopted_commit: TEMPLATE_SOURCE_COMMIT_AT_ADOPTION` with the **actual Starter source commit** used to generate/adopt the project. `freeze_stack_lock.py` intentionally fails while the placeholder remains; it never substitutes the downstream project's own HEAD.

See [AI adoption and upgrade workflow](docs/AI_ADOPTION_WORKFLOW.md).

## GitHub Template Repository

This repository is configured as a GitHub Template Repository. New projects can start with **Use this template**, then record the real Starter source revision and complete composition through the adoption plan.


`make upstream-check` fresh-reads the pinned upstream manifests over GitHub and verifies that the declared AHICP/PPF/Vault Interface profiles and versions actually exist at those revisions. This is intentionally a live integration check rather than a copied profile catalog.
