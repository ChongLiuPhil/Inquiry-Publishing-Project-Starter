# Inquiry Publishing Stack: ecosystem and agent entrypoint

This repository is the composition entrypoint for four logically independent components:

| Component | Responsibility | Public entry |
| --- | --- | --- |
| AHICP | Human-led, AI-assisted inquiry and creation governance | [homepage](https://chongliuphil.github.io/AI-Assisted-Human-Inquiry-and-Creation-Protocol/) · [repository](https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol) |
| PPF | Source-centered publishing, releases, archives, and Continuous Web | [homepage](https://chongliuphil.github.io/Personal-Publishing-Framework/) · [repository](https://github.com/ChongLiuPhil/Personal-Publishing-Framework) |
| Vault Interface | Provider-neutral public metadata schemas and validators | [homepage](https://chongliuphil.github.io/Vault-interface/) · [repository](https://github.com/ChongLiuPhil/Vault-interface) |
| Starter | Composition, adoption, profiles, and upgrades | [homepage](https://chongliuphil.github.io/Inquiry-Publishing-Project-Starter/) · [repository](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter) |

These components remain logically independent. Cross-linking them creates discoverability and a shared adoption path; it does not transfer normative authority from one component to another.

## Understanding the stack vs configuring a project

The ecosystem intentionally separates two entry roles:

- **Understand the stack through AHICP:** the [AHICP public homepage](https://chongliuphil.github.io/AI-Assisted-Human-Inquiry-and-Creation-Protocol/) explains what the system is for and how to begin.
- **Configure through Starter:** an AI uses this repository’s `ecosystem.yaml`, profiles, stack files, and Agent Retrieval Contract for project composition, adoption, upgrades, deployment, and reconstruction.

AHICP explains the method and user experience; Starter keeps the precise machine contract. They link to each other without replacing each other.

## Default configuration baseline

The default for a newly configured project is:

~~~text
AHICP (full)
+ PPF (full)
+ Vault Interface (public metadata adapter)
+ project-specific content
~~~

The project records actual adoption in project-stack.yaml; it does not create competing copies of upstream normative sources.

The full-research-publication profile is the default new-project profile. Reduced profiles remain available, but an AI agent must use one only after explicit human selection. Apparent project simplicity is not authorization to silently omit AHICP or PPF.

The Vault Interface is an adapter, not a replacement for AHICP or PPF.

## Privacy and publication boundary

- Unpublished manuscripts, original research, personal working memory, credentials, and other copyright-bearing source assets are private by default.
- Public framework repositories contain reusable methods, schemas, templates, validators, and approved public documentation—not private project state.
- A private source repository may still have a Continuous Web publication.
- Unpublished or transitional Web output is restricted by default.
- Reader authentication belongs at the access layer. Repository files contain only a policy reference, never a password, API token, private key, OTP, recovery code, or other secret.
- A shared reader credential may exist as a transitional operational policy, but its secret value stays provider-side.
- Moving a publication from restricted to public requires explicit human authorization and does not imply making the source repository public.
- The private control plane is referenced only through authorized project configuration. It is not copied into this public Starter.

## Human and AI discoverability

Every public component should expose the same four public homepages and point to the same canonical ecosystem contract.

For machine-oriented discovery, use:

- [ecosystem.yaml](../ecosystem.yaml)
- [AGENT_RETRIEVAL_CONTRACT.md](AGENT_RETRIEVAL_CONTRACT.md)
- [llms.txt](llms.txt)

A public link can make the ecosystem discoverable, but no webpage can force every arbitrary AI system to crawl additional resources. The contract therefore defines the expected behavior for an agent that follows repository instructions.

## Agent retrieval contract

When an AI agent enters through any component homepage or repository, it must:

1. identify the current component and read that repository's ecosystem.yaml;
2. read the canonical Starter ecosystem and [AGENT_RETRIEVAL_CONTRACT.md](AGENT_RETRIEVAL_CONTRACT.md);
3. resolve the roles and public entrypoints of all four components;
4. for a downstream project, read its selected Starter profile, project-stack.yaml, and lock file;
5. fresh-read each active upstream manifest at its pinned revision;
6. inspect private project state only after explicit human authorization;
7. preserve the distinction between proposal, authorization, execution, verification, and durable write-back.

Following public links is a retrieval protocol, not permission to access private repositories or private deployment systems.

## Continuous Web and Cloudflare

The detailed operational contract is [CONTINUOUS_WEB_CLOUDFLARE.md](CONTINUOUS_WEB_CLOUDFLARE.md), with a Chinese mirror at [CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md](CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md). The minimal-human execution path is [CLOUDFLARE_MINIMAL_HUMAN_HANDOFF.md](CLOUDFLARE_MINIMAL_HUMAN_HANDOFF.md), and the browser-agent handoff is [CLOUDFLARE_WORK_AGENT_HANDOFF.md](CLOUDFLARE_WORK_AGENT_HANDOFF.md).

Before asking a human to perform a Cloudflare action, an AI agent must give numbered operator-level steps, identify the exact target account/project/domain and affected layer, explain credential scope and data transmission, state what must not be shared with the AI, define verification evidence, and provide a rollback path.

Provider-specific details should be taken from the current PPF Cloudflare runbooks and, when needed, verified against the live provider UI or current official documentation rather than guessed.
