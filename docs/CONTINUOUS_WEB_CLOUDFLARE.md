# Continuous Web and Cloudflare operational guide

For a new project, first read [PROJECT_PROVISIONING_CONTRACT.md](PROJECT_PROVISIONING_CONTRACT.md), then [CLOUDFLARE_MINIMAL_HUMAN_HANDOFF.md](CLOUDFLARE_MINIMAL_HUMAN_HANDOFF.md). For browser-capable execution, use [CLOUDFLARE_WORK_AGENT_HANDOFF.md](CLOUDFLARE_WORK_AGENT_HANDOFF.md). The machine-readable non-secret plan is [../templates/cloudflare-access-plan.yaml](../templates/cloudflare-access-plan.yaml).

This guide is a reusable operational contract, not a claim that every project has already been deployed.

## 1. Separate the four layers

~~~text
private source repository
    -> validation and build
    -> Cloudflare deployment
    -> reader-access policy
~~~

Keep these decisions separate:

- Source privacy — whether canonical source and original work are private.
- Deployment identity — which credential may build or deploy.
- Reader access — who may read the deployed Web output.
- Search visibility — whether crawlers may index the output.

Changing one layer must not silently change another. In particular, making the Web publication public does not require making the canonical GitHub repository public.

## 2. Default private-project posture

For unpublished, research, manuscript, or other copyright-bearing work:

1. Keep the canonical repository private.
2. Keep full AHICP and full PPF active unless the human explicitly selects a reduced profile.
3. Use a private CI or Cloudflare-side Git integration; do not copy source into a public repository.
4. Deploy only the intended rendered output.
5. Keep the Web publication restricted until explicit public-release authorization.
6. Put reader authentication in Cloudflare Access or an equivalent server-side gate.
7. Store only an access-policy reference in project files. Never store the actual password, token, private key, recovery code, or other secret in Git or chat.
8. Disable indexing for restricted material and verify that previews, assets, feeds, generated files, and alternate hostnames follow the same access policy.

A single shared reader credential may be used as a temporary policy, but it is a shared secret. The secret itself must remain provider-side. Prefer centrally managed, short-lived, or individually revocable credentials as sensitivity or audience size grows.

## 3. Declarative project state

A private new project should normally begin with a publication contract equivalent to:

~~~yaml
source:
  visibility: private

publication:
  web:
    mode: continuous
    enabled: true
    authorization_state: not-authorized
    visibility: restricted
    access:
      mode: authenticated
      implementation: cloudflare-access
      policy_ref: shared-reader-access

deployment:
  web:
    provider: cloudflare-workers
    enabled: false
    status: staged
~~~

policy_ref identifies the intended policy. It is not a place to store credential material.

## 4. Deployment profiles

Choose and record one profile before deployment:

- **Workers Builds Native + private-project-quota-saver — default for ordinary new projects.** The user may complete one short project-level GitHub ↔ Cloudflare connection. Cloudflare then owns the Git-triggered production build/deploy connection and provider-managed build credential. Content-only changes do not start GitHub Actions, configuration PRs use one lightweight contract check, main pushes do not duplicate the Web build in GitHub Actions, and heavy GitHub validation is manual.
- **Agent-provisioned external CI — optional advanced profile.** Use when the project explicitly needs an account-owned individual-Worker `Editor` deployment credential, reusable platform authorization, and the Trusted Secret Broker.
- **Future/provider-specific profile** — use only after current provider documentation and a real test confirm its capability.

The default profile is intentionally optimized for practical setup simplicity rather than account-wide zero-touch provisioning. Deployment credential scope and reader access remain separate security decisions.

## 5. Required setup sequence

For an ordinary new project:

1. Identify the exact personal GitHub repository, output directory, Cloudflare account, and target Worker/project.
2. Confirm the source repository is private.
3. Use `workers-builds-native` + `private-project-quota-saver` unless the human explicitly selected the advanced profile.
4. Create or confirm the private repository under `ChongLiuPhil`.
5. In Cloudflare Workers & Pages, import/connect that repository.
6. If GitHub asks, authorize the Cloudflare Git integration for the target repository.
7. Configure production branch `main`, root directory `/`, `bash scripts/cloudflare_build.sh`, and `npx wrangler deploy`.
8. Keep preview/non-production builds disabled by default.
9. Run the first deployment.
10. Protect the Worker with Worker-scoped Cloudflare Access using **All traffic**, unless a verified account-wide Access policy already covers it.
11. Verify the deployed revision, anonymous denial/challenge, authenticated reader access, and representative direct assets.
12. Make one harmless content-only source change and push to `main`.
13. Verify Workers Builds automatically deploys the new revision without renewed GitHub or Cloudflare authorization and without a duplicate GitHub Actions production Web build.
14. Configure a custom domain only after separate domain/DNS authorization.
15. Record verified non-secret provider state and rollback evidence.

If the advanced external-CI profile is selected, follow the pinned PPF External-CI and Trusted Secret Broker contracts instead.

## 6. Required AI-agent handoff format

Before any Cloudflare action that requires human account-owner interaction, the agent must provide a numbered handoff. Each handoff must contain:

1. Target — exact account, project/Worker, repository, hostname/domain, and environment.
2. Effect — whether the step changes deployment, DNS, routing, access, indexing, or performs read-only inspection.
3. Where to click — the current Dashboard area and navigation path. If the recorded path may be stale, verify current UI or provider documentation first.
4. What to select or enter — exact non-secret values from project configuration, with placeholders only where a human-owned value is required.
5. Secret boundary — explicitly identify values that must never be pasted into chat.
6. Completion evidence — what the human should see in the UI when the step succeeds.
7. Agent resume point — what provider/repository state the agent will verify next.
8. Rollback — how to reverse the change if it affects publication, access, DNS, or routing.

Vague instructions such as “configure Cloudflare,” “enable Access,” or “set up DNS” are insufficient.

## 7. GitHub + Cloudflare project integration

For the default route, per-project Cloudflare Git authorization is allowed and expected when the Cloudflare GitHub App does not yet have access to the target repository.

Read the current pinned PPF runbooks:

- `docs/PER_PROJECT_GITHUB_CLOUDFLARE_SETUP.md` — default per-project operator flow;
- `docs/CI_COST_POLICY.md` — private-repository GitHub Actions / build-minute policy;
- `docs/CLOUDFLARE_GITHUB_AUTHORIZATION.md` — Native default plus optional advanced authorization model;
- `docs/CLOUDFLARE_SECURITY_PROFILES.md` — deployment-credential trade-offs;
- `docs/CLOUDFLARE_ACCESS_PROFILE.md` — publication visibility to reader-access mapping;
- `docs/AGENT_PROVISIONED_EXTERNAL_CI.md` — optional advanced profile only.

Do not require account-wide platform provisioning just to start an ordinary project. Conversely, do not weaken project privacy merely because a repository connection needs human consent.

## 8. Restricted reader-access setup

Before a restricted publication is considered safe:

1. Confirm the hostname or route to protect.
2. Create or select the access application/policy for that hostname.
3. Choose the intended authentication mechanism or audience rule.
4. Apply the policy to production and any preview or alternate routes that can expose the same restricted material.
5. Keep any shared credential or identity secret entirely outside Git and chat.
6. Test as an unauthenticated reader in a fresh private/incognito session: access must be denied or challenged.
7. Test as an authorized reader: access must succeed.
8. Request a known asset, feed, or direct generated-file URL while unauthenticated to verify there is no bypass.
9. Verify restricted pages are not intended for indexing.
10. Write only the non-secret policy reference and verified result back to private project state.

## 9. Public cutover

Moving a site from restricted to public is a publication decision, not merely a technical toggle.

Before cutover:

1. confirm explicit human public-release authorization;
2. verify that rendered output contains only approved public material;
3. verify that private working memory, credentials, unpublished assets, and source-only files are absent;
4. update the access policy;
5. test anonymous access;
6. verify search and canonical behavior as intended;
7. record the new publication state.

The source repository may remain private after public cutover.

## 10. Secrets and credential handling

The agent must never request that a human paste a password, API token, private key, recovery code, or other credential into chat.

If a provider UI requires a secret:

1. tell the human exactly which provider field requires it;
2. tell the human to enter it directly in the provider UI;
3. state that the value must not be sent back to the AI;
4. verify only non-secret resulting state afterward.

## 11. Completion gate

A Continuous Web setup is complete only when:

- repository validation and build gates pass;
- the deployed URL is reachable under the intended policy;
- restricted content is not anonymously readable;
- public content is not accidentally restricted;
- direct assets and alternate routes do not bypass access control;
- the production authorization state is correct;
- rollback is known;
- verified provider state has been written back to private project records.
