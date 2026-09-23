# Event-driven unified publication

## Authorization and behavior

On 2026-09-23 the human approved replacing hourly polling with commit-triggered updates for the four framework repositories, plus explicit registration of future deliverables. Other repositories are not automatically enrolled. Main-site anonymous reading is authorized; canonical URLs, DNS, old sites and paid plans are unchanged.

Every upstream default-branch push sends a notification without path filtering. Starter accepts `repository / branch / revision` through workflow_dispatch, verifies registered public sources, the default branch and commit ancestry, then reconciles all current heads. Notifications are hints, never URLs or commands. Delayed events cannot select an old revision. Reconciling all sources handles GitHub concurrency replacing pending runs from different repositories. There is no background schedule; manual recovery remains available.

Unchanged outputs make no commit or deployment. Changed outputs are pinned to full SHAs, tested, built and validated before committing the lock. Push conflicts fail without force-pushing; rerun after repair. Failed builds retain the last successful site. Starter main updates use the existing Cloudflare Git integration. Bot pushes do not start normal GitHub push workflows, so validation runs inside refresh; Cloudflare delivery of bot pushes requires real acceptance testing.

## One-time owner setup

1. Open https://github.com/settings/personal-access-tokens/new . Name: `inquiry-starter-sync`; recommended expiration: 90 days, then rotate.
2. Resource owner: `ChongLiuPhil`. Select only `Inquiry-Publishing-Project-Starter`.
3. Add only repository **Actions: Read and write**, plus automatic Metadata read. Do not add Contents write. Actions write also manages other Actions in the repository; it is not restricted to one dispatch endpoint.
4. Enter the generated value directly as `STARTER_SYNC_TOKEN` in each Actions secret form below. Never send the value to the agent, Git, PRs or logs:
   - https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol/settings/secrets/actions/new
   - https://github.com/ChongLiuPhil/Personal-Publishing-Framework/settings/secrets/actions/new
   - https://github.com/ChongLiuPhil/Vault-interface/settings/secrets/actions/new
5. Seeing the secret name in all three repositories completes entry. Successful notification means accepted by Starter, not deployed. The agent must verify the notification, lock commit, Cloudflare build and live version.

The secret is supplied only to the notification step with no checkout or project build. Builds do not receive it. Revoke the token or remove these secrets to stop notifications; manually run Starter refresh to recover missed updates. Missing or expired credentials must fail visibly.

## Publication manifest and complete deliverables

`site/publications.json` owns publication scope; `site/sources.lock.json` pins source versions. Existing components retain approved static-files lists rather than copying entire docs trees. Register a future book or application under a unique publications key with repository, branch, visibility: public, source_directory, output_directory, build and mount. Add the same key under publications in the lock with repository and full revision. Install both templates/publication-source-changed.yml and templates/notify-starter.yml as workflows, replace OWNER/REPOSITORY in both with the registered repository, and configure its secret. The push marker has no credentials. A workflow_run follow-up from the default branch verifies canonical repository, branch and success before dispatch, including Dependabot pushes. It downloads no artifacts, restores no caches and checks out no source code. Forks skip by default and require explicit enrollment. Renaming the default branch still triggers notification; Starter reports configuration drift until the registered branch is updated.

Supported builders are static-directory and quarto. Every chapter, image, script, stylesheet and download in the complete output directory is included; normal additions/deletions need no per-file registration. Require index.html; reject traversal, symlinks, hidden files, mount collisions and excess size. Use mount-compatible relative URLs; validation checks local links in all HTML. Limits: 25 MiB per file and 200 MiB total. Exceeding them fails without purchasing storage.

Examples in templates/publication-examples/static and quarto are not live publications. In an independent example repository, public or _book is the sole output directory. Quarto is pinned to 1.10.18: a missing or different runtime fails. When registering a Quarto publication, provision that exact runtime in both validation and Cloudflare build environments; never skip rendering. Current framework delivery has no Quarto dependency. build_local runs a temporary example checkout; build_remote retrieves a public immutable revision.

The Quarto subprocess receives no inherited tokens, user HOME or Git configuration; its output is not printed. This is credential hygiene, not a sandbox for hostile code. Register only approved public build configurations. Private projects use their own restricted publication flow, not this public-source fetcher.

## Acceptance and rollback

Record offline tests, real fixed-source builds, GitHub CI and live commit-to-deployment separately. Live acceptance requires upstream notification, source revisions, Starter commit, Cloudflare build/version and live build-info.json. Content-neutral events must produce no lock commit or deployment. Token entry is required before claiming this complete.

Rollback uses revert PRs or a verified Worker version. Repair and rerun failed notifications/builds; do not restore cron. On exhausted free quota, stop for quota recovery or a separate human decision; never upgrade automatically.
