# Unified Cloudflare Workers delivery

Status: holding deployed; full runtime and Workers Builds unverified; canonical URL cutover not authorized. This v3 contract supersedes the Pages-specific migration procedure, including its requirement to protect the current main site with Access.

## Approved target

Four independent repositories compose one website on Worker `inquirystack`, at `https://inquirystack.philohub.workers.dev`. `/` is the human entry; `/agent/` is the machine entry. GitHub remains the canonical source. Only Starter is connected to Git; the other three public repositories are fetched without credentials at `site/sources.lock.json` revisions. Website source locks and downstream adoption locks remain separate.

The user explicitly authorized public anonymous reading on the current main site on 2026-09-22. Do not require a main-site reader allowlist or create an Everyone Access rule. This does not authorize changing ecosystem canonical URLs, About Websites, DNS, or retiring GitHub Pages. Existing Pages holding is retained. Other projects keep their existing access modes. Free-first: no purchase or paid upgrade; a verified provider-native URL may become permanent after separate explicit canonical cutover approval.

## Repository configuration

Use `cloudflare-builds.yaml`, `package-lock.json` and `wrangler.jsonc` at the intended Git revision. Root `/`, main branch `main`, assets `_site`. Build: `npm ci --ignore-scripts --no-audit --no-fund && python tools/build_public_site.py`; deploy: `npm run cloudflare:deploy`; non-production: `npm run cloudflare:preview`. Toolchain targets are Python 3.12.12, Node 22.22.0, Wrangler 4.136.1. Read actual build logs to verify versions; configuration alone is not runtime evidence.

The holding alternative adds `--holding` to the Python command. Current runtime holding was a direct API bootstrap, not a Git-triggered build. Do not represent its version as a Starter checkout.

## Cloud execution

1. Read the [cloud-only handoff](CLOUDFLARE_WEB_AGENT_HANDOFF.md) and fresh-read provider state. Reuse the existing Worker and account subdomain; do not change the account-wide subdomain or create a duplicate project.
2. Review and merge the repository PR after its checks. Do not need local files: GitHub source and Actions artifacts are sufficient. Use the PR head before merge if reviewing a pending implementation.
3. Connect only Starter through the existing Cloudflare GitHub App. New repository grants remain human-owned. Apply the build settings above using native Workers Builds. Never reuse another project's named build credential without verifying its intended scope. Create/select a provider-managed token through the provider UI or secure credential path; no secret may enter Git, chat or logs. Native user-token credentials are not per-Worker least privilege.
4. Keep non-production builds and preview URLs disabled initially. The account's Access bootstrap and preview audience are still unresolved. Do not expose a preview just to pass a test. When approved, configure `preview_worker` Access protection, check higher-priority hostname policies, then enable preview URLs and non-production builds together in provider settings and Wrangler configuration. A real version preview must be challenged anonymously and readable by an approved identity. The preview deploy command must upload a version without replacing main.
5. Run the full main build, record the actual commit and provider deployment/version IDs, and verify anonymous access to `/`, `/agent/`, all component routes, language switching, mobile, no-JavaScript content, JSON, bootstrap, CSS and `/build-info.json`. Compare all four source revisions. Keep existing official URLs and candidate notices intact.
6. Verify an actual Git push triggers the configured build and that replaying reconciliation creates no duplicate connections/triggers/policies. A manual build alone does not establish Git event integration.
7. Record actual results separately from proposal and local/CI results. The broader reusable PPF lifecycle and password mode remain pending as listed in the handoff.

## Rollback

Before a new deployment, re-read the active deployment and save its non-secret version reference. The observed known holding version is recorded in the handoff; recheck that it exists before using it. Restore a verified holding or prior version if the candidate fails, then verify the served content. Pause automatic triggers if necessary. Never force a rollback past changed secrets without inspecting the impact. Revert repository changes via PR; preserve Pages holding, GitHub Pages, existing domains and unrelated App grants. No force push or project deletion.

## Current official references

Checked 2026-09-22; verify live schemas and UI before mutations:

- [Workers best practices](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/)
- [Workers Builds API](https://developers.cloudflare.com/workers/ci-cd/builds/api-reference/)
- [Worker and preview Access protection](https://developers.cloudflare.com/workers/configuration/cloudflare-access/)
- [workers.dev](https://developers.cloudflare.com/workers/configuration/routing/workers-dev/)
- [Static asset billing](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/)
