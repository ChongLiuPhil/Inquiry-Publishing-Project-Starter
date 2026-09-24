# Project Provisioning Acceptance

**Purpose:** live acceptance for the default `workers-builds-native` guided project bootstrap.

This acceptance is intentionally project-scoped. It does not require account-wide zero-touch provisioning.

## Preconditions

- the project request validates;
- the intended GitHub owner is `ChongLiuPhil`;
- the repository is or will be private;
- the project uses the pinned PPF revision;
- public release is not authorized;
- previews are disabled by default.

The public `platform-authorization.yaml` template may remain `unconfigured` for this default profile.

## Acceptance sequence

1. Create or confirm a private repository under `ChongLiuPhil`.
2. Apply the full Starter composition and pinned upstream revisions.
3. Validate the generated PPF `project.infrastructure.json`.
4. Confirm the profile is `workers-builds-native`.
5. In Cloudflare Workers & Pages, import/connect the intended GitHub repository.
6. If GitHub asks, authorize the Cloudflare Git integration for that repository.
7. Configure production branch `main`, root `/`, the pinned PPF build command, and deploy command.
8. Keep non-production/preview builds disabled.
9. Save/deploy and record non-secret Worker/repository connection identifiers.
10. Protect the Worker with Cloudflare Access using **All traffic**, unless verified account-wide Access already protects it.
11. Verify the GitHub repository is still private.
12. Verify the first build/deployment succeeds.
13. Verify the deployed revision matches the intended Git revision.
14. Verify an anonymous production request is challenged or denied.
15. Verify an authenticated approved reader can access the publication.
16. Verify direct asset URLs do not bypass Access.
17. Make one harmless source change and push it to `main`.
18. Verify Workers Builds starts automatically and deploys the new revision.
19. Confirm step 18 required no renewed GitHub repository authorization and no renewed Cloudflare connection.
20. Verify Access remained enforced after the second deployment.
21. Record a rollback/restore point and non-secret provider state.

## Pass criteria

The project passes only when all of these are true:

- repository owner is `ChongLiuPhil`;
- repository visibility is private;
- Workers Builds is connected to the intended repository;
- production branch is `main`;
- the first restricted deployment is verified;
- Worker-scoped Access or explicitly recorded verified account-wide Access is active;
- anonymous access is denied/challenged;
- direct assets remain protected;
- a second push auto-deploys the new revision;
- the second push requires no provider reauthorization;
- no credential value appears in Git/chat/logs;
- rollback/restore evidence is recorded;
- `public_release: NOT AUTHORIZED`.

## Failure handling

If the repository is not visible in Cloudflare, ask the human only to adjust the Cloudflare GitHub App repository access, then re-read provider state.

If the Worker is anonymously reachable, stop private-readiness claims and ask the human to enable/repair Cloudflare Access.

If the second push does not deploy automatically, the project bootstrap is incomplete even if the first deployment succeeded.

Do not solve these failures by requesting that a provider token be pasted into chat.

## Optional advanced acceptance

The advanced `agent-provisioned-external-ci` profile keeps its own stricter acceptance requirements, including Trusted Secret Broker and granular-token evidence. Those requirements are not prerequisites for the default Native path.
