# Project Provisioning Acceptance

**Purpose:** live acceptance for the default `workers-builds-native` guided project bootstrap.

This acceptance is intentionally project-scoped. It does not require account-wide zero-touch provisioning.

## Preconditions

- the project request validates;
- the intended GitHub owner is `ChongLiuPhil`;
- the repository is or will be private;
- the project uses the pinned PPF revision;
- the project request declares `ci_cost_profile: private-project-quota-saver`;
- public release is not authorized;
- previews are disabled by default.

The public `platform-authorization.yaml` template may remain `unconfigured` for this default profile.

## Acceptance sequence

1. Create or confirm a private repository under `ChongLiuPhil`.
2. Apply the full Starter composition and pinned upstream revisions.
3. Validate the generated PPF `project.infrastructure.json`.
4. Confirm the infrastructure profile is `workers-builds-native` and the CI cost profile is `private-project-quota-saver`.
5. Confirm content-only changes do not match any automatic GitHub Actions workflow and configuration PRs targeting `main` match only the lightweight project contract check.
6. In Cloudflare Workers & Pages, import/connect the intended GitHub repository.
7. If GitHub asks, authorize the Cloudflare Git integration for that repository.
8. Configure the Cloudflare Worker/application name to exactly match `wrangler.jsonc.name`, then configure production branch `main`, root `/`, the pinned PPF build command, and deploy command.
9. Keep non-production/preview builds disabled.
10. Save/deploy and record non-secret Worker/repository connection identifiers.
11. If Cloudflare Zero Trust is not yet enabled on this account, complete the one-time Zero Trust setup; later projects reuse it.
12. Protect the Worker with Cloudflare Access using **All traffic**, unless verified account-wide Access already protects it. Reuse an already-approved authentication policy when available.
13. Verify the GitHub repository is still private.
14. Verify the Cloudflare Worker/application name matches `wrangler.jsonc.name`.
15. Verify the first build/deployment succeeds.
16. Verify the deployed revision matches the intended Git revision.
17. Verify an anonymous production request is challenged or denied.
18. Verify an authenticated approved reader can access the publication.
19. Verify direct asset URLs do not bypass Access.
20. Make one harmless **content-only** source change and push it to `main`.
21. Verify Workers Builds starts automatically and deploys the new revision.
22. Verify that step 21 did **not** start an automatic GitHub Actions production Web build.
23. Confirm step 21 required no renewed Git-account connection, Cloudflare GitHub App authorization, or repository connection.
24. Verify Access remained enforced after the second deployment.
25. Record a rollback/restore point and non-secret provider state.

## Pass criteria

The project passes only when all of these are true:

- repository owner is `ChongLiuPhil`;
- repository visibility is private;
- Workers Builds is connected to the intended repository;
- the Cloudflare Worker/application name matches `wrangler.jsonc.name`;
- production branch is `main`;
- `ci_cost_profile` is `private-project-quota-saver`;
- content-only changes do not trigger automatic GitHub Actions;
- configuration PRs targeting `main` are limited to the lightweight contract gate;
- main pushes do not duplicate the production Web build in GitHub Actions;
- heavy GitHub workflows are manual;
- automatic success artifacts are not uploaded and manual publication artifacts default to one-day retention;
- Zero Trust is enabled when Worker-level Access is used;
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

If a content-only change starts GitHub Actions or a main push starts a duplicate GitHub production Web build, treat that as CI-cost policy drift and repair the workflow triggers before acceptance.

If the private Actions allowance is exhausted, optional/manual GitHub heavy checks may remain deferred. Do not solve quota exhaustion by repeatedly triggering blocked runs, and do not enable paid Actions usage or alter billing without explicit human authorization.

Do not solve these failures by requesting that a provider token be pasted into chat.

## Optional advanced acceptance

The advanced `agent-provisioned-external-ci` profile keeps its own stricter acceptance requirements, including Trusted Secret Broker and granular-token evidence. Those requirements are not prerequisites for the default Native path.
