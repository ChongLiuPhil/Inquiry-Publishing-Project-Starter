# Cloudflare public-delivery migration

**Status:** repository-side migration prepared; provider authorization is still required.

## Goal

Move the four public framework sites from GitHub Pages to **Cloudflare Pages** while keeping GitHub as the canonical source, review, versioning, and CI provider.

The four sites are:

- AHICP public introduction / Human Entry;
- PPF public site;
- Vault Interface public site;
- Starter public site, including the stable `/agent/` machine entry.

This migration does **not** change the normative ownership of AHICP, PPF, Vault Interface, or Starter.

## Why Cloudflare Pages

These four sites are static content served from each repository's `docs/` directory. Cloudflare Pages is therefore the preferred delivery target:

- GitHub-connected automatic production deployments;
- preview deployments for branches and pull requests;
- Cloudflare Access for restricted previews;
- custom domains for a provider-independent public identity;
- no Worker runtime requirement for the current static sites.

Use Workers only when runtime logic is actually required. Do not move a static framework site to Workers merely because Workers are available.

## Current state vs target state

Current:

~~~text
GitHub repository
  -> GitHub Pages
  -> chongliuphil.github.io/... public URL
~~~

Target:

~~~text
GitHub repository (canonical source)
  -> Cloudflare Pages (delivery)
  -> custom domain (stable public identity)
~~~

GitHub Pages remains the current public entry until the Cloudflare deployment is verified. A `*.pages.dev` URL may be used for staging, but should not become the permanent ecosystem identity when a custom domain can be used.

The machine-readable plan is [`templates/cloudflare-public-delivery.yaml`](../templates/cloudflare-public-delivery.yaml).

## Default Pages build settings

For all four current framework sites:

~~~text
Production branch: main
Root directory: .
Build command: exit 0
Build output directory: docs
Framework preset: none
~~~

Cloudflare's static-site documentation supports a no-framework deployment and an explicit no-op build command. The deployed content is the repository's existing `docs/` directory.

## Preview policy

Preview deployments are useful, but should not become accidental public publication surfaces.

Default:

~~~text
preview deployments: enabled
preview visibility: restricted
access layer: Cloudflare Access
production framework sites: public
~~~

This is separate from the downstream-project default. A private or unpublished downstream project still defaults to restricted/authenticated production Web until explicit public-release authorization.

## Human-reserved bootstrap

Because there is no authenticated Cloudflare control-plane connection in the current agent environment, the account owner must perform the provider bootstrap:

1. Sign in to Cloudflare and complete MFA.
2. Authorize the Cloudflare Workers & Pages GitHub App for these four repositories. Prefer selected repositories only.
3. For each repository, create/import a Cloudflare Pages project using the build settings above.
4. Record the resulting project name and `*.pages.dev` staging URL.
5. Decide the stable custom-domain layout. Do not change ecosystem public URLs yet.
6. If the domain/zone is not already in Cloudflare, complete the required DNS/zone authorization.
7. Return the non-secret project names and staging/custom-domain URLs to the agent. Never provide API tokens, passwords, private keys, recovery codes, or other secrets in chat.

After those gates, an authorized agent should perform the remaining verification and metadata cutover when tools permit.

## Verification before cutover

Do not replace any current public entrypoint until all of the following are true:

- all four Cloudflare production deployments match the intended `main` revisions;
- each homepage loads;
- AHICP still exposes the full Human Entry and start action;
- Starter `/agent/`, `/agent/entry.json`, bootstrap files, and `llms.txt` resolve on the target domain;
- cross-project links resolve;
- preview deployments are restricted as intended;
- no secret appears in Git, PRs, build logs, or chat;
- rollback to the current GitHub Pages URLs is documented.

## Atomic public-URL cutover

Once the Cloudflare targets and custom domains are verified, update the public identity as one coordinated change:

- GitHub About Website fields;
- all four `ecosystem.yaml` files;
- all four `docs/llms.txt` files;
- Starter `docs/agent/entry.json`;
- Starter Agent Retrieval Contract;
- cross-project homepage links;
- README references where they represent the public landing rather than the canonical GitHub source.

The canonical GitHub repository URLs remain unchanged.

## GitHub Pages during migration

Do not disable GitHub Pages before the Cloudflare cutover is verified.

Before cutover, GitHub Pages is the production fallback.

After cutover, GitHub Pages may remain temporarily available for rollback or be redirected/de-emphasized later. Removing it is a separate cleanup action, not part of initial Cloudflare validation.

## Rollback

Before URL cutover, rollback means simply continuing to use the existing GitHub Pages public entries.

After cutover, rollback means restoring the previous public URLs/DNS and ecosystem metadata. Do not delete Cloudflare projects as part of an emergency rollback; preserve them for diagnosis until the public entry has been restored.
