# AI Adoption and Upgrade Workflow

This file is the operational entry point for future AI agents.

Before using this workflow, read docs/ECOSYSTEM.md, ecosystem.yaml, and docs/AGENT_RETRIEVAL_CONTRACT.md.

## New projects

1. Use full-research-publication as the default profile: full AHICP + full PPF + Vault Interface. A reduced profile requires explicit human selection.
2. For original or unpublished work, create or retain the canonical source as private by default. Do not infer public source visibility from a future public Web publication.
3. Read project-stack.yaml, the selected profile, stack/source-map.yaml, and stack/managed-paths.yaml.
4. Record the actual Starter source commit in starter.adopted_commit; never substitute the downstream repository HEAD.
5. Run python tools/stack.py adoption-plan --json.
6. For every active component, fresh-read its manifest at template_source_commit. The pinned upstream manifest is authoritative for file ownership.
7. For a deferred component explicitly selected by the human, do not copy its template, do not invent an adopted revision, and keep its lock entry null.
8. Compose the project. Prefer functional mapping of reliable existing files over duplicate truth sources.
9. Preserve human approvals, research decisions, publication authorization, canonical identity, and provider actual state.
10. For a project with Continuous Web, default unpublished or transitional Web visibility to restricted and reader access to an authenticated policy reference such as shared-reader-access. Never store the secret credential in Git.
11. Keep deployment staged and publication not authorized until access, preview, verification, and human publication gates are complete.
12. Run stack, governance, build, publication, and runtime gates relevant to the project.
13. Apply changes through a branch and pull request.
14. Run python tools/freeze_stack_lock.py only after all source revisions are explicit and then sync any private portfolio summary.

## Existing-project upgrades

1. Read the current stack and lock and identify active or deferred component state.
2. Reconstruct the four-component ecosystem and fresh-read the project and each target upstream manifest at the proposed template source revision.
3. Use the upstream manifest itself for ownership classification; Starter does not maintain a copied aggregate.
4. Update upstream-managed files only where the pinned manifest permits it.
5. Three-way compare merge-managed paths.
6. Never automatically overwrite project-owned paths.
7. Keep template_source_commit separate from project_adopted_commit; upgrading a template does not silently change the framework revision the project previously approved.
8. Preserve source privacy, access policy, authorization, and provider actual state unless a human explicitly changes them.
9. Do not change a private source repository to public merely because Web output becomes public.
10. Open a PR and run all relevant project gates, including runtime verification when a live provider is affected.
11. After merge, refresh the lock and portfolio-level health summary.

## Cloudflare handoff

When a Cloudflare step requires human action, follow docs/CONTINUOUS_WEB_CLOUDFLARE.md. Provide exact numbered steps, identify the secret boundary, state completion evidence, and explain what the agent will verify afterward. Do not hand back routine machine-operable work merely because Cloudflare is involved.

## Suggested human instruction

> Check the target GitHub repository against my Inquiry Publishing Project Stack. Default to full AHICP + full PPF + Vault Interface. Keep original or unpublished source private, prepare Continuous Web with restricted authenticated access, preserve existing content, approved decisions, publication authorization, access-policy references, and provider actual state, and create a verified upgrade PR. Use a reduced profile only if I explicitly select it. For any Cloudflare step I must perform, give exact numbered UI instructions, tell me which secrets must stay out of chat, and define the completion condition you will verify afterward.
