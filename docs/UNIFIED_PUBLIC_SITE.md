# Unified public delivery: decision and implementation

## Approved architecture decision (2026-09-22)

The human explicitly approved four independent GitHub repositories composed into one website, delivered by one active Cloudflare Worker; a free provider-native address may become permanent after explicit approval, with a custom domain optional. The human entry is `/`; the machine entry is `/agent/`. Authorization covers reversible repository implementation, PRs, validation and durable write-back, not domain selection, account consent, DNS changes or final public cutover.

This supersedes the former four-Pages-project topology, not the independent normative authorities. AHICP remains the main human-conceptual content authority; Starter owns machine retrieval, composition and upgrades. PPF and Vault Interface retain their own authority. Downstream projects do not inherit this framework website's visibility or provider choice.

## Content and routes

`/` is derived directly from the complete human introduction at the pinned AHICP revision. Its substantive explanations, language switch and Chinese no-JavaScript fallback are preserved; shared navigation and candidate notices are added. `/ahicp/` retains a component entry; `/ppf/`, `/vault-interface/` and `/starter/` compose the complete upstream public homepages. `/start/` provides a brief start path. `/agent/`, its descriptor, bilingual bootstrap files and `/llms.txt` are independently retrievable without browser interaction.

The website is a delivery layer, not a fourth specification or independently editable normative copy. Documents outside the explicit public-output allowlist link to upstream GitHub. Never copy entire `docs/` trees, Working Memory, manuscripts or private projects into the site.

## Reproducible build

```sh
python tools/build_public_site.py
```

Output: `_site/`. The build does not replace the legacy `docs/` homepage, deploy, edit GitHub About, or change DNS.

`site/sources.lock.json` pins full commit SHAs for three remote public upstreams. Starter uses the actual build checkout and records its real SHA, avoiding a self-referential repository lock. This lock controls website composition, not `project-stack.yaml`, `template_source_commit` or `project_adopted_commit`.

Only explicitly allowed repositories and files are read, using credential-free HTTPS for remote sources. `build-info.json` records all four source revisions, input/output SHA-256 hashes, the lock digest and whether tracked working-tree changes exist. Retrieval or validation failure fails the build; no stale-cache or floating-main fallback substitutes for a pin.

Source updates are event-driven, never scheduled. Default-branch pushes in the three upstreams notify Starter using a dedicated fine-grained token limited to Starter Actions write. Starter validates the event, reconciles current public default-branch heads, compares publication outputs, validates a changed site and commits immutable source pins. Duplicate or content-neutral updates do not deploy. Every event reconciles all sources so replaced pending runs cannot lose an update from another repository. See [event setup and acceptance](EVENT_DRIVEN_PUBLICATION.md).

Publication scope lives in `site/publications.json`. Existing framework pages retain their approved explicit files; registered books and applications use complete output directories, including newly generated chapters, binary assets and downloads. Registration/publication expansion is reviewed; routine changes within an approved output directory require no per-file approval. Quota exhaustion stops publication; paid upgrades are never automatic.

## Current versus candidate state

The current official human and machine entries remain GitHub Pages until cutover is separately approved. The candidate descriptor preserves `public_landing` and `human_entry` while `delivery_candidate` exposes relative paths. The Workers address may become canonical only after verification and explicit cutover approval.

Candidate output includes migration notices and `noindex`. **Noindex is not authentication.** The builder intentionally supports only candidate/holding modes, not unauthorized production. Final cutover needs a separately authorized coordinated change to public URLs, candidate notices, indexing rules and related validators.

## Validation and recovery

`Unified public site` CI runs offline regression tests, a real pinned-upstream build, link/script/provenance checks, and desktop/mobile/no-JavaScript browser checks. It retains candidate artifacts and screenshots. It has no Cloudflare credentials or deployment step. CI PASS does not establish provider Access PASS.

Worker holding is deployed. Subsequent human authorization permits anonymous main-site reading without an Access allowlist. Deploy the full candidate after build validation; previews stay disabled until protection and audience approval are verified. Canonical URL cutover still needs separate approval. See the [migration guide](CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.md).

Roll back repository changes through an ordinary revert PR, never a force push. Before cutover, keep every current GitHub Pages URL. Restore the holding page or a previously verified candidate deployment as needed; do not delete Cloudflare projects or revoke App permissions used by unrelated projects.
