# AI Adoption and Upgrade Workflow

This file provides a single operational entry point for future AI agents.

## New projects

1. Read `project-stack.yaml`, the selected `profiles/*.yaml`, `stack/source-map.yaml`, and `stack/managed-paths.yaml`.
2. Run `python tools/stack.py adoption-plan --json`.
3. Fresh-read each component from the repository and revision declared by the plan, using its template root and manifest.
4. Compose the project for the selected profile. Replace placeholders, but do not copy upstream specifications or READMEs into a second project truth source.
5. Run the project-local stack, governance, build, and publication checks.
6. Apply changes through a branch and pull request.
7. After adoption, run `python tools/freeze_stack_lock.py` to freeze resolved revisions.
8. If a private portfolio manages the project, sync only its registry summary. Registration does not imply publication.

## Existing-project upgrades

1. Read the current `project-stack.lock.yaml` to identify the previous upstream revisions.
2. Fresh-read the current project and the target upstream manifests.
3. Update `upstream-managed` paths from the target revision when appropriate.
4. Use a base/current/new three-way comparison for `merge-managed` paths.
5. Never automatically overwrite `project-owned` paths.
6. Prefer functional mapping of reliable existing files over creating duplicate truth sources.
7. Preserve publication authorization, canonical identity, provider actual state, and human-approved decisions unless the human explicitly changes them.
8. Open a pull request and run all project gates; when a live Web provider is involved, include runtime verification where relevant.
9. After merge, refresh the lock and any portfolio-level stack summary.

## Suggested human instruction

> Check the target GitHub repository against my Inquiry Publishing Project Stack; choose the profile appropriate to its existing complexity; preserve existing content, approved decisions, publication authorization, and provider actual state; prefer functional mapping; create and verify an upgrade PR. Hand back only identity authorization, account-owner confirmation, or UI actions the available tools cannot perform.
