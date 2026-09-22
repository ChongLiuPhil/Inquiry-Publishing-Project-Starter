# Cloudflare unified public-delivery migration

**State: repository preparation; provider actual state unverified; no public cutover.**

On 2026-09-22 the human approved one unified website and one Pages project instead of four Pages projects. The four GitHub repositories retain independent specifications, history, PRs and CI. See [UNIFIED_PUBLIC_SITE.md](UNIFIED_PUBLIC_SITE.md) and the [machine-readable plan](../templates/cloudflare-public-delivery.yaml).

## One website, two entry roles

On one custom domain still to be selected, `/` is the AHICP-led human entry and `/agent/` is the Starter machine entry. Component sections are `/ahicp/`, `/ppf/`, `/vault-interface/` and `/starter/`; `/start/` explains how to begin. These are approved target paths, not existing canonical URLs.

GitHub remains canonical source. Keep the four GitHub Pages URLs, human/machine entries and About Websites unchanged. Pages is appropriate for this static framework site; downstream PPF projects still choose Pages, Workers or another provider according to runtime needs.

## Build settings

Connect only `ChongLiuPhil/Inquiry-Publishing-Project-Starter`. Three other public upstreams are fetched without credentials at locked SHAs; this build does not require expanding the GitHub App's repository scope.

```text
Production branch: main
Root directory: .
Framework preset: none
Initial build command: python tools/build_public_site.py --holding
Full candidate build command: python tools/build_public_site.py
Build output directory: _site
PYTHON_VERSION: 3.12
NODE_VERSION: 22
```

The previous `exit 0` + `docs` settings do not compose the unified site. Deploy only the empty holding page before Access is verified. A Dashboard Production label for main does not mean an ecosystem public cutover.

## Minimal human gates and agent resumption

1. Open `https://dash.cloudflare.com/`, sign in, complete MFA directly, and select the actual target account. Never send passwords, MFA codes, tokens, cookies, private keys or recovery codes in chat.
2. Inspect **Workers & Pages** for an existing corresponding Pages project; do not duplicate or delete projects. For a new connection use **Create application → Pages → Connect to Git / Import an existing Git repository**. This is Pages, not a Worker's Deploy command flow. Recheck official documentation/live UI if labels differ.
3. At the GitHub App authorization page select `ChongLiuPhil`; add only Starter for this task. Do not remove grants used by other actual projects. Completion means Cloudflare can see Starter. After account-owner authorization, an agent with genuinely callable authenticated tools should resume routine configuration. A human browser login does not automatically create an agent control-plane session.
4. Configure/create **one** Pages project using the initial settings above. No project name has been selected or assumed available. Keep automatic production/preview deployments off while configuring Access; deploy only the holding page. Non-secret feedback consists of project name, actual `pages.dev` URL and deployment status; no token is needed in chat.
5. **Settings → General → Enable access policy** covers the preview default policy only. Follow the official Known issues exact-hostname procedure to protect `project.pages.dev`, while retaining/recreating protection for `*.project.pages.dev`; verify both in Zero Trust Applications. Approve reader identities directly in Cloudflare, without Everyone allow rules. Wildcard preview protection does not secure the main hostname; noindex is not authentication.
6. Verify anonymous/incognito requests cannot read the exact hostname or a real preview, while an approved identity can. Check direct files, JSON, bootstrap, static assets and alternate hostnames. If no preview exists, leave that check pending, not PASS.
7. After Access verification, the agent changes to the full candidate build command and performs a restricted deployment. Check the Starter and three pinned revisions in `/build-info.json`, all sections, language switching, no-JavaScript fallback, guide loading and machine resources. Persist only non-secret project identifiers, URLs, revisions and observed results. Access IDs, reader identities and other private control-plane state remain in authorized private provider state.
8. Only then does the human select a custom domain and authorize necessary DNS/zone work. Domain validation and final public cutover are separate gates: do not automatically remove Access, change public URLs or disable GitHub Pages.

## Final public cutover (not authorized)

The builder intentionally supports holding/candidate behavior only. Canonical/public fields retain existing entries; relative candidate paths are separate. After explicit final approval, prepare a coordinated PR set covering four-repository ecosystem metadata, About Websites, public README links, llms, machine descriptor, retrieval contract, cross-links and old-URL mappings. Update candidate notices, indexing policy and corresponding validators. GitHub source repository URLs do not change.

Four repositories cannot form a truly atomic cross-repository Git transaction. Record the cutover checklist and each repository revision, retain old entries during a compatibility window and verify each update; do not describe coordination as an indivisible atomic operation.

## Verification and rollback

Passing GitHub build/browser CI verifies candidate artifacts, not Cloudflare deployment, TLS, DNS or Access.

Before cutover, keep all old GitHub Pages URLs. Restore the holding build or last verified candidate deployment and pause automatic builds when needed. Roll back repository changes through a revert PR. After cutover, restore recorded entries, About Websites and DNS from the checklist. Never delete projects or force-push history as incidental cleanup. Re-read provider actual state after operations; proposals do not establish execution.

## Official operational references

Checked: 2026-09-22. Recheck live UI at execution time.

- https://developers.cloudflare.com/pages/configuration/git-integration/
- https://developers.cloudflare.com/pages/configuration/preview-deployments/
- https://developers.cloudflare.com/pages/platform/known-issues/
- https://developers.cloudflare.com/pages/configuration/branch-build-controls/
- https://developers.cloudflare.com/pages/configuration/build-configuration/
