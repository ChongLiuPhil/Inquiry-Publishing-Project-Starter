# Inquiry Publishing Stack: ecosystem and agent entrypoint

This repository is the composition entrypoint for four logically independent components:

| Component | Responsibility | Public entry |
| --- | --- | --- |
| AHICP | Human-led, AI-assisted inquiry and creation governance | [homepage](https://chongliuphil.github.io/AI-Assisted-Human-Inquiry-and-Creation-Protocol/) · [repository](https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol) |
| PPF | Source-centered publishing, releases, archives, and Continuous Web | [homepage](https://chongliuphil.github.io/Personal-Publishing-Framework/) · [repository](https://github.com/ChongLiuPhil/Personal-Publishing-Framework) |
| Vault Interface | Provider-neutral public metadata schemas and validators | [repository](https://github.com/ChongLiuPhil/Vault-interface) |
| Starter | Composition, adoption, profiles, and upgrades | [homepage](https://chongliuphil.github.io/Inquiry-Publishing-Project-Starter/) · [repository](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter) |

## Default configuration baseline

Every newly configured project should be able to adopt a complete AHICP governance layer and the complete PPF publishing layer. The project records its actual adoption in `project-stack.yaml`; it does not create competing copies of the upstream normative source.

The normal full profile is:

```text
AHICP (full) + PPF (full) + Vault Interface (public metadata) + project-specific content
```

The Vault Interface is an adapter, not a replacement for AHICP or PPF. A project may defer a component only when its lock and profile state say so explicitly.

## Privacy and publication boundary

- Unpublished manuscripts, original research, personal working memory, credentials, and other copyright-bearing source assets are private by default.
- Public repositories contain reusable methods, schemas, templates, validators, and documentation—not private project state.
- A private project may still have a Continuous Web publication. Protect it with an access-control layer; never place a password or secret in the repository or client-side source.
- The private control plane is referenced only through authorized project configuration. It is not copied into this public Starter.

## Agent retrieval contract

When an AI agent enters through any component homepage or repository, it should:

1. Read this file and `ecosystem.yaml`.
2. Identify the current component and then read the AHICP and PPF upstream entrypoints.
3. Read the selected Starter profile and lock file.
4. Fresh-read each active upstream manifest at its pinned revision.
5. Inspect private project state only after explicit human authorization.
6. Preserve the distinction between proposal, authorization, execution, verification, and durable write-back.

Following the public links is a retrieval protocol, not permission to access private repositories or private deployment systems.

## Continuous Web and Cloudflare

The detailed operational guide is [`CONTINUOUS_WEB_CLOUDFLARE.md`](CONTINUOUS_WEB_CLOUDFLARE.md), with a Chinese mirror at [`CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md`](CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md).

An AI agent must explain the selected Cloudflare architecture, deployment credential scope, reader-access policy, secrets handling, verification gates, and rollback path before asking a human to perform any non-delegable Cloudflare action.
