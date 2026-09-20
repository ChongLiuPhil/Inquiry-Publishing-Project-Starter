# Continuous Web and Cloudflare operational guide

For the shortest human handoff, read [CLOUDFLARE_MINIMAL_HUMAN_HANDOFF.md](CLOUDFLARE_MINIMAL_HUMAN_HANDOFF.md). For browser-capable execution, use [CLOUDFLARE_WORK_AGENT_HANDOFF.md](CLOUDFLARE_WORK_AGENT_HANDOFF.md). The machine-readable non-secret plan is [../templates/cloudflare-access-plan.yaml](../templates/cloudflare-access-plan.yaml).

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

- Native provider integration — simplest operational path; validate the provider-managed credential scope and do not describe it as least privilege unless verified.
- Hardened external CI — GitHub Actions or another CI uses an account-owned token restricted to the target Worker or project; keep the token only in the CI secret store.
- Future/provider-specific profile — use only after current provider documentation and a real test confirm its capability.

PPF security-profile documents provide the reference trade-offs. Deployment credentials and reader access remain orthogonal.

## 5. Required setup sequence

1. Identify the exact GitHub source repository, output directory, canonical domain, visibility, retention policy, Cloudflare account, and target Worker/project.
2. Confirm that the source repository is private when it contains unpublished original work.
3. Select the build and deployment profile.
4. Create or connect the Cloudflare project without exposing secrets to the repository.
5. Configure build commands and output paths from repository-owned machine contracts.
6. Configure preview behavior.
7. Configure reader access before exposing unpublished output.
8. Configure a custom domain only with the temporary authority required for provisioning.
9. Run a preview build and verify HTML, assets, feeds, redirects, headers, alternate URLs, and access behavior.
10. Run production deployment only after the human approves the publication state.
11. Record verified provider state, deployment revision, access-policy reference, and verification result in private project state.
12. Preserve rollback paths for build, access policy, and domain routing.

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

## 7. Cloudflare ↔ GitHub connection

For the PPF reference implementation, detailed operator runbooks live in the PPF repository:

- docs/CLOUDFLARE_GITHUB_AUTHORIZATION.md — account-owner and GitHub App authorization flow;
- docs/CLOUDFLARE_SECURITY_PROFILES.md — deployment credential profiles and least-privilege trade-offs;
- docs/CLOUDFLARE_ACCESS_PROFILE.md — mapping of publication visibility to reader-access configuration;
- docs/CLOUDFLARE_OBSERVED_UI_MAPPING.md — dated observations of Cloudflare UI fields.

An agent should read these before giving provider-specific clicks or field mappings.

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
