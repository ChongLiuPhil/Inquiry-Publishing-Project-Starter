# Unified Cloudflare Workers delivery

Status: the full public candidate and GitHub-triggered update passed acceptance. The owner has approved the `workers.dev` canonical URL cutover; this version still requires live checks after deployment before it can be marked `verified-cutover`. Preview remains disabled and has not passed Access acceptance. See the [candidate acceptance record](CLOUDFLARE_DEPLOYMENT_ACCEPTANCE.md) for previous revisions and evidence.

## Approved target

Four independent repositories compose one website on Worker `inquirystack`, at `https://inquirystack.philohub.workers.dev`. `/` is the human entry; `/agent/` is the machine entry. GitHub remains the canonical source. Only Starter is connected to Git; the other three public repositories are fetched without credentials at `site/sources.lock.json` revisions. Website source locks and downstream adoption locks remain separate.

The owner authorized public anonymous reading and separately approved `https://inquirystack.philohub.workers.dev/` as the canonical human entry and `/agent/` as the machine entry. Do not add a main-site reader allowlist or Everyone Access rule. Keep former GitHub Pages and Pages holding available. No DNS change, domain purchase or paid upgrade is authorized. Other projects retain independent access modes.

## Repository configuration

Use `cloudflare-builds.yaml`, `package-lock.json` and `wrangler.jsonc` at the intended Git revision. Root `/`, main branch `main`, assets `_site`. Build: `npm ci --ignore-scripts --no-audit --no-fund && python tools/build_public_site.py`; deploy: `npm run cloudflare:deploy`; non-production: `npm run cloudflare:preview`. Toolchain targets are Python 3.12.12, Node 22.22.0, Wrangler 4.136.1. Read actual build logs to verify versions; configuration alone is not runtime evidence.

The holding alternative adds `--holding` to the Python command. The original Worker holding was a direct API bootstrap, not a Git-triggered build. The current main Worker serves the full Starter Git-built candidate; do not mistake historical holding for the current version.

## Cloud execution

1. Read the [cloud-only handoff](CLOUDFLARE_WEB_AGENT_HANDOFF.md) and [acceptance record](CLOUDFLARE_DEPLOYMENT_ACCEPTANCE.md), then fresh-read provider state. Reuse the existing Worker, build connection and account subdomain.
2. Native Workers Builds already connects only Starter and builds the complete main site on `main` updates. New repository grants remain human-owned. The native user build token is not per-Worker least privilege; keep all secrets out of Git, chat and logs.
3. The publishing GitHub App is installed on the four selected repositories. Scoped installation tokens notify Starter and create source-lock PRs; ordinary checks gate merge and native Builds deploys it. No scheduled polling is configured. See the [App contract](GITHUB_APP_PUBLICATION.md) for permissions and recovery.
4. Preview URLs and non-main builds remain disabled. After a preview audience is approved, protect `preview_worker` with Access, inspect higher-priority hostname policies, then enable previews and non-main builds together. Verify anonymous denial and approved-reader access on a real version preview. Preview upload must not replace main.
5. After this canonical deployment, compare actual revision, `/build-info.json`, `/agent/entry.json`, every component route, bilingual and no-JavaScript content. Check canonical links, `robots.txt`, and response headers for removal of candidate `noindex`. Mark `verified-cutover` only after live acceptance; otherwise restore the previous verified Worker version and revert the repository change.

## Rollback

Before a new deployment, re-read the active deployment and save its non-secret version reference. If a candidate fails, restore the prior verified Worker version from private deployment state or revert the source-lock PR through normal checks, then verify the served response. Historical holding needs a fresh availability check before use. Pause triggers if necessary. Never force a rollback past changed secrets without inspecting the impact. Preserve Pages holding, GitHub Pages, existing domains and unrelated App grants. No force push or project deletion.

## Current official references

Checked 2026-09-22; verify live schemas and UI before mutations:

- [Workers best practices](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/)
- [Workers Builds API](https://developers.cloudflare.com/workers/ci-cd/builds/api-reference/)
- [Worker and preview Access protection](https://developers.cloudflare.com/workers/configuration/cloudflare-access/)
- [workers.dev](https://developers.cloudflare.com/workers/configuration/routing/workers-dev/)
- [Static asset billing](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/)
