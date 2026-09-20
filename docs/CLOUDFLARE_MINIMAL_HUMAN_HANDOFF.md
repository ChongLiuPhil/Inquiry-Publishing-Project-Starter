# Cloudflare minimal-human handoff

**Status:** canonical operator handoff for private/restricted Continuous Web  
**Policy reference:** `shared-reader-access`

This guide reduces Cloudflare work to the smallest practical set of human-reserved actions. Everything else should be performed by an authorized API-capable agent or by a browser agent such as ChatGPT Work when available.

## 1. Canonical access model

The canonical policy is **not a repository password**. It is a reusable Cloudflare Access policy named `shared-reader-access`.

For human readers, the preferred low-friction model is:

~~~text
restricted hostname
-> Cloudflare Access
-> shared-reader-access reusable policy
-> explicit allowed reader email(s)
-> One-Time PIN
-> 24h session
~~~

The policy name is shared; reader identities and provider IDs remain private provider state.

Current Cloudflare Access documentation is identity-policy based. A generic static shared password is not a native Access policy selector. Therefore a pre-existing shared password is treated as a **legacy compatibility credential**, not the canonical Access mechanism. Never move that secret into Git merely to preserve the old UX.

## 2. Human actions that should remain human

A human should normally need to perform only these actions:

1. Sign in to Cloudflare and complete MFA.
2. **Once per GitHub account/organization:** authorize the Cloudflare Workers & Pages GitHub App for the selected repository or repositories.
3. **Once per automation principal:** create the initial scoped API token(s). Enter or copy the token only into the secure tool/secret store that will execute the automation; never paste it into chat or commit it.
4. Confirm the intended reader identity set. If OTP is used, enter the allowed email addresses directly in Cloudflare or in the secure agent form.
5. If an existing deployment still uses a legacy shared static password, enter that secret directly into the existing provider-side secret field only. Do not send the value to the AI.
6. Approve the final restricted-to-public publication cutover when and if publication should become public.

Everything else is expected to be agent-operable and verifiable.

## 3. One-time Cloudflare ↔ GitHub authorization

For Workers Builds, Cloudflare's current flow is:

1. Cloudflare Dashboard → **Workers & Pages**.
2. Open the Worker, then **Settings → Builds → Connect**.
3. Choose **GitHub**.
4. Install/authorize the **Cloudflare Workers and Pages** GitHub App.
5. Prefer **selected repositories only** and select only the project repositories that Cloudflare must build.
6. Return to Cloudflare and confirm that the Git repository is shown under the Worker's build settings.

This is the main unavoidable account-owner browser authorization. After it exists, Workers Builds can be managed programmatically through Cloudflare's Builds API.

## 4. One-time API automation credentials

For an API-capable agent, create narrowly scoped user tokens in **My Profile → API Tokens → Create Token → Custom token**.

### Access application and policy token

Required permission:

~~~text
Account → Access: Apps and Policies → Edit
~~~

Limit the token to the intended Cloudflare account where possible.

### Identity-provider token

Only needed when the agent must create or modify OTP/IdP configuration:

~~~text
Account → Access: Organizations, Identity Providers, and Groups → Edit
~~~

If the identity provider is already configured, do not grant this extra permission.

### Workers Builds token

Cloudflare's Builds API currently requires a **user-scoped** API token:

~~~text
Account → Workers Builds Configuration → Edit
Account → Workers Scripts → Read
~~~

The first permission manages triggers/build settings. Workers Scripts Read is used to resolve the immutable Worker tag.

Do not use a Global API key.

## 5. Reader authentication: recommended OTP path

If One-Time PIN is not already available:

1. Cloudflare Dashboard → **Zero Trust → Integrations → Identity providers**.
2. Under **Your identity providers**, choose **Add new identity provider**.
3. Choose **One-time PIN**.
4. Save.
5. Do not enable broad `Everyone` or `all valid emails` access merely to make OTP work.

Create the reusable policy:

1. **Zero Trust → Access controls → Policies**.
2. Select **Add a policy**.
3. Policy name: `shared-reader-access`.
4. Action: **Allow**.
5. Session duration: **24 hours** initially.
6. Include: **Emails** → add only approved reader email addresses.
7. Require: **Login Methods** → **One-time PIN**.
8. Save.

The 24-hour value is a starting security/usability balance; later changes are a policy decision, not a template migration.

## 6. Protect one publication hostname

For each restricted publication:

1. **Zero Trust → Access controls → Applications**.
2. Select **Create new application**.
3. Select **Self-hosted and private**.
4. Select **Add public hostname**.
5. Enter the project's canonical restricted hostname. Protect the entire hostname unless the project contract intentionally specifies narrower paths.
6. Under **Access policies**, attach the existing reusable policy `shared-reader-access`.
7. Select the intended login provider, normally One-Time PIN.
8. Set the application session duration to the intended value, normally 24 hours initially.
9. Save the application.
10. Verify the Access application appears for the exact hostname before exposing unpublished output.

Cloudflare Access is deny-by-default for a protected application: a reader must match an Allow policy.

## 7. Agent/API execution after the human bootstrap

Once the GitHub App and scoped API token exist, an API-capable agent should do the routine work:

1. Read the project's `publishing.yaml`, `cloudflare-builds.yaml`, Worker name, repository ID, branch, build command, deploy command, preview command, and hostname.
2. Inspect current Cloudflare actual state.
3. Create or update `shared-reader-access` through the Access API.
4. Create or update the self-hosted Access application for the hostname.
5. Connect/configure Workers Builds after the GitHub App authorization already exists.
6. Trigger a preview build.
7. Verify build revision, runtime URL, Access behavior, direct assets, feeds, and alternate routes.
8. Write only non-secret IDs/status back into private project state.
9. Stop before public cutover unless the human has explicitly authorized publication.

## 8. Browser-agent / ChatGPT Work mode

If direct Cloudflare API tooling is unavailable, use **Work mode** with the prompt in `CLOUDFLARE_WORK_AGENT_HANDOFF.md`.

The human should take over only when Cloudflare asks for:

- sign-in/MFA;
- GitHub App authorization;
- API token secret capture/secure storage;
- reader identity approval;
- direct entry of an existing legacy password/secret;
- final public-release approval.

After each human-reserved action, return control to the agent so it can continue configuration and verification.

## 9. Legacy shared static password

If a current deployment already has one shared static reading password:

- do **not** paste it into chat;
- do **not** encode it into `publishing.yaml`, `website.yaml`, `wrangler.jsonc`, CI variables committed to Git, or Access policy metadata;
- if the existing runtime has a provider-side secret field, the human may enter the current value there directly as a temporary compatibility layer;
- do not build a new static-password gate unless preserving that exact UX is a deliberate project requirement;
- prefer migrating human readers to Access identity + OTP, while keeping `shared-reader-access` as the stable policy reference.

## 10. Verification gate

Restricted Continuous Web is not complete until all are true:

- anonymous private/incognito request is challenged or denied;
- an approved reader can authenticate and read;
- an unapproved reader cannot read;
- a direct asset/feed/generated-file URL cannot bypass Access;
- preview and production endpoints have the intended protection;
- deployed revision matches the intended source revision;
- no reader secret appears in Git, build logs, PRs, or chat;
- rollback is known;
- private project state records the Access application ID/policy ID and verification result, but no credential value.
