# Inquiry Publishing Stack: ecosystem and agent entrypoint

This repository is the composition entrypoint for four logically independent components:

| Component | Responsibility | Public entry |
| --- | --- | --- |
| AHICP | Human-led, AI-assisted inquiry and creation governance | [homepage](https://inquirystack.philohub.workers.dev/) · [repository](https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol) |
| PPF | Source-centered publishing, releases, archives, and Continuous Web | [homepage](https://inquirystack.philohub.workers.dev/ppf/) · [repository](https://github.com/ChongLiuPhil/Personal-Publishing-Framework) |
| Vault Interface | Provider-neutral public metadata schemas and validators | [homepage](https://inquirystack.philohub.workers.dev/vault-interface/) · [repository](https://github.com/ChongLiuPhil/Vault-interface) |
| Starter | Composition, adoption, project-provisioning orchestration, profiles, and upgrades | [homepage](https://inquirystack.philohub.workers.dev/starter/) · [repository](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter) |

These components remain logically independent. Cross-linking them creates discoverability and a shared adoption path; it does not transfer normative authority from one component to another.

## Understanding the stack vs configuring a project

The ecosystem intentionally separates two entry roles:

- **Understand the stack through AHICP:** the [AHICP public homepage](https://inquirystack.philohub.workers.dev/) explains what the system is for and how to begin.
- **Configure through Starter:** an AI uses this repository’s `ecosystem.yaml`, profiles, stack files, Agent Retrieval Contract, and Project Provisioning Contract for project composition, adoption, low-touch provisioning, upgrades, deployment, and reconstruction.

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

The preferred ordinary new-project infrastructure profile is `workers-builds-native` with `private-project-quota-saver`: a private repository under the personal `ChongLiuPhil` account, one short human-assisted Cloudflare Git connection for that project, Worker-scoped Access by default, and previews disabled until their own protection is accepted. Content-only changes do not start GitHub Actions; configuration PRs use one lightweight contract gate; `main` does not run a duplicate GitHub Web build; heavy GitHub workflows are manual; Cloudflare Workers Builds owns the automatic production Web build. After the first restricted deployment, a second content-only push must auto-deploy without renewed authorization or duplicate GitHub Actions production build before the connection is considered operationally verified. Public release, repository publication, reader expansion, domain/DNS authority, provider-scope expansion, paid Actions usage, and billing changes remain human-reserved.

`agent-provisioned-external-ci` remains available as an optional advanced profile when one-Worker deployment-credential isolation is worth the additional platform authorization and Trusted Secret Broker infrastructure.

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
- [PROJECT_PROVISIONING_CONTRACT.md](PROJECT_PROVISIONING_CONTRACT.md)
- [llms.txt](llms.txt)

A public link can make the ecosystem discoverable, but no webpage can force every arbitrary AI system to crawl additional resources. The contract therefore defines the expected behavior for an agent that follows repository instructions.

## Agent retrieval contract

When an AI agent enters through any component homepage or repository, it must:

1. identify the current component and read that repository's ecosystem.yaml;
2. read the canonical Starter ecosystem and [AGENT_RETRIEVAL_CONTRACT.md](AGENT_RETRIEVAL_CONTRACT.md);
3. resolve the roles and public entrypoints of all four components;
4. for a downstream project, read its selected Starter profile, `project-stack.yaml`, lock file, and `project-provisioning.yaml` when present;
5. for a new project, read the Project Provisioning Contract, the pinned PPF per-project setup contract, and the pinned PPF CI Cost Policy; read private platform-authorization state only if the optional advanced profile is explicitly selected;
6. fresh-read each active upstream manifest at its pinned revision;
7. inspect other private project state only after explicit authorization;
8. preserve the distinction between proposal, authorization, execution, verification, and durable write-back.

Following public links is a retrieval protocol, not permission to access private repositories or private deployment systems.

## Public delivery provider

The four public framework sections now use **one Cloudflare Worker** at `https://inquirystack.philohub.workers.dev/`; GitHub remains the canonical source/version-control provider. The former framework GitHub Pages sites are retired; the previous verified Worker version is the rollback point.

Use [CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.md](CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.md) and the machine-readable [cloudflare-public-delivery.yaml](../templates/cloudflare-public-delivery.yaml) for the approved cutover, its live verification and rollback. The selected `workers.dev` identity is free; a custom domain remains optional.

Future domain or visibility changes remain separate decisions with verification and rollback.

## Continuous Web and Cloudflare

The new-project orchestration contract is [PROJECT_PROVISIONING_CONTRACT.md](PROJECT_PROVISIONING_CONTRACT.md). The detailed Cloudflare operational contract is [CONTINUOUS_WEB_CLOUDFLARE.md](CONTINUOUS_WEB_CLOUDFLARE.md), with a Chinese mirror at [CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md](CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md). The default execution path is the documented per-project Workers Builds bootstrap; browser-agent and advanced automation handoffs remain optional implementation aids.

Starter records provisioning intent and authorization boundaries; PPF remains authoritative for executable GitHub/Cloudflare provider logic. Provider credential plaintext must never enter the language model. The default Workers Builds path keeps its deployment credential provider-managed.

Before asking a human to perform a Cloudflare action, an AI agent must give numbered operator-level steps, identify the exact target account/project/domain and affected layer, explain credential scope and data transmission, state what must not be shared with the AI, define verification evidence, and provide a rollback path.

Provider-specific details should be taken from the current PPF Cloudflare runbooks and, when needed, verified against the live provider UI or current official documentation rather than guessed.
