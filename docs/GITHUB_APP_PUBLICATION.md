# Account-installed GitHub App publication

This is the default commit-notification mechanism. It replaces distributing a personal access token to upstream Actions. It does not remove authentication: a private App key and webhook secret remain in Cloudflare Worker Secrets. GitHub installation tokens are created on demand, expire within one hour, and are never persisted or logged.

## Scope and setup

1. In https://github.com/settings/apps/new create `Inquiry Publishing ChongLiuPhil`, only installable on the current account. Homepage: this Starter repository. Leave OAuth callbacks, user authorization and device flow disabled/unset.
2. Keep Webhook active and SSL verification enabled. URL: `https://inquirystack.philohub.workers.dev/_events/github`. The owner generates a strong random secret in their password manager and enters it directly in the Secret field. Never put it in chat or Git.
3. Repository permissions: **Contents read-only**, **Actions read and write**, mandatory Metadata read-only; no other account/organization/repository permissions. Subscribe only to **Push**. The owner submits creation and installation. Install on selected repositories: Starter, AHICP, PPF, Vault-interface. This App's maximum permissions apply to every installed repository, not just Starter. Runtime tokens further restrict Actions write to Starter alone; no Contents write is requested.
4. In the App settings, the owner generates a private key and stores it directly in Cloudflare **Workers & Pages → inquirystack → Settings → Variables and Secrets**, type Secret, name `GITHUB_APP_PRIVATE_KEY` (complete PEM). Store the same webhook secret as Secret `GITHUB_APP_WEBHOOK_SECRET`. Record the App ID as non-secret text `GITHUB_APP_ID`. These are Worker runtime secrets, never Build variables or upstream Actions secrets. Do not expose their values to the agent. The agent may configure the non-secret App ID.
5. Redeliver the initial ping after saving all settings. A 200 verifies the signature path; it does not prove the push/deployment chain. Disable/remove the legacy upstream PAT notification workflows so each push has one notification path. No PAT creation is needed.

The target remains one active `inquirystack` Worker on `philohub.workers.dev`. Only `/_events/*` invokes Worker code first; normal static reads retain the assets-first path. No DNS, canonical URL, reader policy or billing change is part of this setup. Missing secrets refuse webhook processing. Existing previews remain disabled pending their separate Access verification.

## Handling, verification and limits

The handler validates HMAC-SHA256 before interpreting push payloads. Only registered public sources and their configured default branch can dispatch. Starter pushes are ignored because native Workers Builds already handles them. Starter independently revalidates repository, branch and SHA; events do not supply commands. Duplicate/late notifications may start a check, but cannot cause duplicate deployments or revert source versions. See [receiver contract](EVENT_DRIVEN_PUBLICATION.md).

Payloads larger than 2 MiB return 413. Invalid signature returns 401, unregistered/private source 403, branch drift 409, missing configuration 503, GitHub API errors 502. A 202 only means accepted or intentionally ignored, not deployed. Check Recent deliveries, Starter refresh logs, source-lock commit, Cloudflare Build and live build-info.json separately. Failed webhook deliveries are not automatically retried by GitHub: after repair, redeliver in App settings or run Starter refresh manually. No cron is introduced. Free Worker request/CPU and GitHub Actions quotas still apply; stop on exhaustion, never upgrade automatically. Webhook requests consume Worker requests even when rejected.

Before claiming acceptance, test a real upstream content-changing commit and a content-neutral commit, verify signed delivery, receiver output comparison, bot lock commit, native Cloudflare build and matching online source/version. Mock tests and a successful bundle do not establish this chain.

## Recovery

To stop automated notifications, suspend the App installation or deactivate its webhook; the last static website remains available. Rotate a compromised webhook secret in both providers, or replace the private key and revoke the old key. Revert the receiver PR to return to assets-only delivery, or restore a verified Worker version; retain manual Starter refresh. Do not restore hourly polling. Installation selection and publication registration are separate: future books/apps require both owner-approved installation access and a manifest entry. Private manuscripts are not added to this public-source App pipeline.
