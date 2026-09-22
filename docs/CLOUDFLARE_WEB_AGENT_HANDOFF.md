# Cloud-only agent continuation

The complete execution checklist is in [the Chinese handoff](CLOUDFLARE_WEB_AGENT_HANDOFF.zh-CN.md). All required sources, configuration and CI artifacts are on GitHub; no originating computer or local files are needed.

## Authorization and current state

Use one Worker, `inquirystack`, on the existing `philohub` account subdomain. Anonymous main-site reading at `https://inquirystack.philohub.workers.dev` is explicitly authorized, superseding the earlier restricted-main candidate plan. Preview remains restricted and disabled until protection is verified. Canonical URL changes, DNS, old-site retirement and paid upgrades are not authorized. Keep Pages holding and GitHub Pages.

Only Starter needs Git integration. Other public upstream files are fetched at `site/sources.lock.json` pins without credentials. Do not conflate website source locks with downstream adoption locks. Source baseline: Starter `117e9981c4d712110800f5d94bb875164fb41689`, PPF `5fca3e99df588c338eca45915478a07a9cadc099`; query the actual PR head and subsequent main revision.

Starter PR head `6a2509de72c5b176f28846442f20fe3266b69d12` passed Ecosystem validation, Stack CI and Unified public site GitHub Actions on 2026-09-22; it remains open. Re-check main before merge. The pinned full-site build and output/provenance validation passed locally; browser verification passed 24 route/viewport combinations (desktop, mobile, JavaScript disabled) including language switching and guide loading. Wrangler 4.136.1 dry-run succeeded with the full generated `_site`. The local Python was 3.9; CI and Workers Builds target 3.12.12, which must be confirmed from actual logs.

A direct-API holding deployment was verified on 2026-09-22 at 09:56 UTC: expected HTTP 503 and Setup pending, no-store/noindex. Holding version `88bb1d9a-acf7-4e52-8cd6-d9dfef3e9f3c`, deployment `a91fbe67-1bd1-4130-bbf4-31bc3dd9f817`. Re-read live state. This is not a Git-triggered or complete-content deployment. Access was not enabled; no protected preview or approved-reader runtime test passed.

## Continue entirely in the cloud

1. Read AGENTS, ecosystem, retrieval contract, v3 migration plan, migration guide and this PR at its current head; inspect GitHub checks before merge. Use Actions artifacts instead of asking for local output.
2. Inspect existing provider state through authorized API/MCP. Browser fallback must first demonstrate control of the existing signed-in session. Reuse the Worker; do not rename the account subdomain or create duplicates.
3. Connect Starter only and apply `cloudflare-builds.yaml`, `wrangler.jsonc` and locked npm dependencies. Resolve a legitimate native user build token through provider UI/secure storage; another project's token name is not evidence of authorization. Never copy secrets into Git, chat or logs.
4. Deploy the full public main site and verify a real Git push triggers the build. Compare actual runtime tools, checkout and all upstream revisions with `/build-info.json`. Verify routes, machine resources, direct assets, bilingual navigation, mobile and no-JavaScript content. Preserve old canonical URLs and candidate/noindex notices.
5. Keep previews disabled until Access team setup and preview audience are approved, then configure preview-only Access and validate a real preview anonymously and as an approved reader. Preview upload must not replace main.
6. Record real deployment and rollback evidence separately from CI and local tests. Private audiences, control-plane state and credential references stay private.

## Reusable standard still pending

This PR is a deployable repository preparation and handoff, not a completed PPF adapter. Implement the originally approved standard through GitHub PRs/Actions: PPF owns provider logic, Starter owns thin orchestration; `doctor / plan / apply / verify / rollback`, configuration inference, idempotent reconciliation, partial-failure recovery, permission/quota/build/drift handling, native Builds default and hardened external-CI alternative. Keep independent source and adoption locks.

Provide public, email Access (OTP/24h) and optional per-project shared-password modes. Existing modes are preserved; new projects default restricted and stay holding before audience approval. Audiences do not automatically transfer between projects. Password mode must use only Cloudflare Secrets, server authentication for every resource with `run_worker_first`, constant-time comparison, signed expiring secure cookies, logout, login rate limiting, rotation invalidation, no shared caching and fail-closed errors/quota exhaustion. Document edge rate-limit scope and request charges. Add bilingual contracts, minimal examples and meaningful tests for bypasses, wrong credentials, expiry, rotation, faults and rollback. Distinguish simulated tests from live verification.

Completion means reusable tooling plus the now-authorized public main site, with protected previews enabled only after validation. Canonical cutover remains separate. Roll back to a verified holding/prior version and recheck; pause triggers as needed, preserve old sites and unrelated grants, never delete projects or force-push.
