# Unified public delivery: decision and implementation

## Approved architecture decision (2026-09-22)

The human approved four independent GitHub repositories composed into one website on one active Cloudflare Worker and later approved `inquirystack.philohub.workers.dev` as its permanent public identity. The human entry is `/`; the machine entry is `/agent/`. DNS changes and paid upgrades remain outside this cutover.

This supersedes the former four-Pages-project topology, not the independent normative authorities. AHICP remains the main human-conceptual content authority; Starter owns machine retrieval, composition and upgrades. PPF and Vault Interface retain their own authority. Downstream projects do not inherit this framework website's visibility or provider choice.

## Content and routes

`/` is derived directly from the complete human introduction at the pinned AHICP revision. Its substantive explanations, language switch and Chinese no-JavaScript fallback are preserved; shared navigation is added. `/ahicp/` retains a component entry; `/ppf/`, `/vault-interface/` and `/starter/` compose the complete upstream public homepages. `/start/` provides a brief start path. `/agent/`, its descriptor, bilingual bootstrap files and `/llms.txt` are independently retrievable without browser interaction.

The website is a delivery layer, not a fourth specification or independently editable normative copy. Documents outside the explicit public-output allowlist link to upstream GitHub. Never copy entire `docs/` trees, Working Memory, manuscripts or private projects into the site.

## Reproducible build

```sh
python tools/build_public_site.py
```

Output: `_site/`. The build does not replace the legacy `docs/` homepage, deploy, edit GitHub About, or change DNS.

`site/sources.lock.json` pins full commit SHAs for three remote public upstreams. Starter uses the actual build checkout and records its real SHA, avoiding a self-referential repository lock. This lock controls website composition, not `project-stack.yaml`, `template_source_commit` or `project_adopted_commit`.

Only explicitly allowed repositories and files are read, using credential-free HTTPS for remote sources. `build-info.json` records all four source revisions, input/output SHA-256 hashes, the lock digest and whether tracked working-tree changes exist. Retrieval or validation failure fails the build; no stale-cache or floating-main fallback substitutes for a pin.

Source updates are event-driven, never scheduled. Default-branch pushes in the three upstreams notify Starter through the account-installed GitHub App and its signed webhook; runtime installation tokens are restricted to Starter Actions write. Starter validates the event, reconciles current public default-branch heads, compares publication outputs, validates a changed site and commits immutable source pins. Duplicate or content-neutral updates do not deploy. Every event reconciles all sources so replaced pending runs cannot lose an update from another repository. See [event setup and acceptance](EVENT_DRIVEN_PUBLICATION.md).

Publication scope lives in `site/publications.json`. Existing framework pages retain their approved explicit files; registered books and applications use complete output directories, including newly generated chapters, binary assets and downloads. Registration/publication expansion is reviewed; routine changes within an approved output directory require no per-file approval. Quota exhaustion stops publication; paid upgrades are never automatic.

## Approved public delivery

The owner approved `https://inquirystack.philohub.workers.dev/` as the public human entry and `/agent/` as the machine entry. The descriptor identifies those routes. GitHub Pages stays online as a legacy route and rollback path.

The builder requires the exact approved Worker and cutover flag in the versioned migration plan. Public output has canonical links and no candidate `noindex` gate; previews remain disabled until separate Access acceptance. The live cutover is recorded as verified only after deployment and route checks pass.

## Validation and recovery

`Unified public site` CI runs offline regression tests, a real pinned-upstream build, link/script/provenance checks, and desktop/mobile/no-JavaScript browser checks. It has no Cloudflare credentials or deployment step. CI PASS does not establish live provider acceptance.

Anonymous main-site reading and canonical use of the selected Worker are approved. Previews stay disabled until protection and audience approval are verified. See the [migration guide](CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.md) for live state.

Roll back repository changes through an ordinary revert PR, never a force push. Keep former GitHub Pages URLs and restore the prior verified Worker version as needed; do not delete Cloudflare projects or revoke App permissions used by unrelated projects.
