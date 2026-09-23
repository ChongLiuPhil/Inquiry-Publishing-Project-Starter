# Event-driven unified publication

## Authorization and behavior

On 2026-09-23 the human approved replacing hourly polling with commit-triggered updates for the four framework repositories, plus explicit registration of future deliverables. Other repositories are not automatically enrolled. Main-site anonymous reading is authorized; canonical URLs, DNS, old sites and paid plans are unchanged.

Every upstream default-branch push sends a notification without path filtering. Starter accepts `repository / branch / revision` through workflow_dispatch, verifies registered public sources, the default branch and commit ancestry, then reconciles all current heads. Notifications are hints, never URLs or commands. Delayed events cannot select an old revision. Reconciling all sources handles GitHub concurrency replacing pending runs from different repositories. There is no background schedule; manual recovery remains available.

Unchanged outputs make no commit or deployment. Changed outputs are pinned to full SHAs, tested, built and validated before committing the lock. Push conflicts fail without force-pushing; rerun after repair. Failed builds retain the last successful site. Starter main updates use the existing Cloudflare Git integration. Bot pushes do not start normal GitHub push workflows, so validation runs inside refresh; Cloudflare delivery of bot pushes requires real acceptance testing.

## Account-installed GitHub App (default)

Use the [GitHub App setup contract](GITHUB_APP_PUBLICATION.md). This supersedes the personal-token setup: upstream repositories need neither a PAT secret nor a notification workflow. The App receives signed push events and requests a short-lived installation token narrowed to Starter Actions write. The existing receiver and Cloudflare Git integration remain unchanged.

## Publication manifest and complete deliverables

`site/publications.json` owns publication scope; `site/sources.lock.json` pins source versions. Existing components retain approved static-files lists rather than copying entire docs trees. Register a future book or application under a unique publications key with repository, branch, visibility: public, source_directory, output_directory, build and mount. Add the same key under publications in the lock with repository and full revision. Authorize the new repository in the App installation after approving its publication manifest. No notification workflow is required. Default-branch changes fail with configuration drift until the manifest is updated. The two notification workflow templates are legacy PAT alternatives only; do not enable both mechanisms. Private sources remain outside this public fetcher.

Supported builders are static-directory and quarto. Every chapter, image, script, stylesheet and download in the complete output directory is included; normal additions/deletions need no per-file registration. Require index.html; reject traversal, symlinks, hidden files, mount collisions and excess size. Use mount-compatible relative URLs; validation checks local links in all HTML. Limits: 25 MiB per file and 200 MiB total. Exceeding them fails without purchasing storage.

Examples in templates/publication-examples/static and quarto are not live publications. In an independent example repository, public or _book is the sole output directory. Quarto is pinned to 1.10.18: a missing or different runtime fails. When registering a Quarto publication, provision that exact runtime in both validation and Cloudflare build environments; never skip rendering. Current framework delivery has no Quarto dependency. build_local runs a temporary example checkout; build_remote retrieves a public immutable revision.

The Quarto subprocess receives no inherited tokens, user HOME or Git configuration; its output is not printed. This is credential hygiene, not a sandbox for hostile code. Register only approved public build configurations. Private projects use their own restricted publication flow, not this public-source fetcher.

## Acceptance and rollback

Record offline tests, real fixed-source builds, GitHub CI and live commit-to-deployment separately. Live acceptance requires upstream notification, source revisions, Starter commit, Cloudflare build/version and live build-info.json. Content-neutral events must produce no lock commit or deployment. App installation, provider secrets and real delivery verification are required before claiming this complete.

Rollback uses revert PRs or a verified Worker version. Repair and rerun failed notifications/builds; do not restore cron. On exhausted free quota, stop for quota recovery or a separate human decision; never upgrade automatically.
