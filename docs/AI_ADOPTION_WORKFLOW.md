# AI Adoption and Upgrade Workflow

This file is the operational entry point for future AI agents.

## New projects

1. Read `project-stack.yaml`, the selected profile, `stack/source-map.yaml`, and `stack/managed-paths.yaml`.
2. Record the actual Starter source commit in `starter.adopted_commit`; never substitute the downstream repository HEAD.
3. Run `python tools/stack.py adoption-plan --json`.
4. For every **active** component, fresh-read its manifest at `template_source_commit`. The pinned upstream manifest is authoritative for file ownership.
5. For a deferred optional component, do not copy its template, do not invent an adopted revision, and keep its lock entry null.
6. Compose the project. Prefer functional mapping of reliable existing files over duplicate truth sources.
7. Preserve human approvals, research decisions, publication authorization, canonical identity, and provider actual state.
8. Run stack, governance, build, publication, and runtime gates relevant to the project.
9. Apply changes through a branch and pull request.
10. Run `python tools/freeze_stack_lock.py` only after all source revisions are explicit and then sync any private portfolio summary.

## Existing-project upgrades

1. Read the current stack and lock and identify active/deferred component state.
2. Fresh-read the project and each target upstream manifest at the proposed template source revision.
3. Use the upstream manifest itself for ownership classification; Starter does not maintain a copied aggregate.
4. Update upstream-managed files only where the pinned manifest permits it.
5. Three-way compare merge-managed paths.
6. Never automatically overwrite project-owned paths.
7. Keep `template_source_commit` separate from `project_adopted_commit`; upgrading a template does not silently change the framework revision the project previously approved.
8. Preserve authorization and provider actual state unless a human explicitly changes them.
9. Open a PR and run all relevant project gates, including runtime verification when a live provider is affected.
10. After merge, refresh the lock and portfolio-level health summary.

## Suggested human instruction

> Check the target GitHub repository against my Inquiry Publishing Project Stack; choose the profile appropriate to its existing complexity; preserve existing content, approved decisions, publication authorization, and provider actual state; prefer functional mapping; create and verify an upgrade PR. Hand back only identity authorization, account-owner confirmation, policy decisions reserved to me, or UI actions the available tools cannot perform.
