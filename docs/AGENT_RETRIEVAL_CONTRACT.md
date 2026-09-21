# Agent Retrieval Contract

## 0. Canonical machine entry

The stable public machine/configuration landing page is:

https://chongliuphil.github.io/Inquiry-Publishing-Project-Starter/agent/

An AI agent may be handed only that URL. It must then retrieve the canonical ecosystem and this contract, reconstruct all four components, and continue according to the rules below. The public landing page is a discovery surface; the GitHub-tracked ecosystem and contracts remain authoritative.

This document is the canonical cross-repository retrieval contract for the Inquiry Publishing Stack.

It does not merge AHICP, PPF, Vault Interface, or the Starter into one normative system. It defines how an AI agent reconstructs their relationship before configuring, upgrading, publishing, or operating a project.

## 1. Entry from any public surface

An agent may enter through any of these surfaces:

- an AHICP, PPF, Vault Interface, or Starter public homepage;
- any of the four GitHub repositories;
- a README, `AGENTS.md`, `ecosystem.yaml`, or `llms.txt`;
- a downstream project that declares adoption of one or more stack components.

From any such entrypoint, the agent must reconstruct the whole public ecosystem before making cross-component configuration decisions.

## 2. Mandatory retrieval sequence

1. Identify the current component.
2. Read that repository's `ecosystem.yaml` and ecosystem documentation.
3. Read this Starter contract and the canonical Starter `ecosystem.yaml`.
4. Resolve all four public components and their roles:
   - AHICP — human-led inquiry and creation governance;
   - PPF — source-centered publishing lifecycle and Continuous Web;
   - Vault Interface — provider-neutral public metadata contract;
   - Starter — composition, adoption, profile, and upgrade layer.
5. For a downstream project, read `project-stack.yaml`, its selected profile, and the lock file.
6. For every active AHICP or PPF component, fresh-read the pinned upstream manifest or template manifest before configuration or upgrade.
7. Retrieve private project state only when the human has explicitly authorized that access.
8. Before any external-state write, distinguish proposal, authorization, execution, verification, and durable write-back.
9. Before any Cloudflare action, follow the shared Continuous Web and Cloudflare operational guide and any PPF provider-specific runbook relevant to the selected deployment profile.

Public-link traversal is a retrieval instruction. It is never authorization to access a private repository, private vault, provider account, credential, unpublished source, or deployment control plane.

## 3. Default new-project baseline

Unless the human explicitly selects a reduced profile, a newly configured project uses:

```text
full AHICP
+ full PPF
+ Vault Interface public metadata adapter
+ project-owned content
```

Reduced profiles remain available for legitimate cases, but selecting one is an explicit human deviation from the default baseline. An agent must not infer a reduced profile merely because a project appears simple.

## 4. Default privacy and publication posture

For original, unpublished, research, manuscript, or other copyright-bearing project content:

- the canonical source repository is private by default;
- Continuous Web may still be prepared and deployed;
- unpublished or transitional Web output is restricted by default;
- reader authentication is implemented at the access layer, not by committing a password to Git;
- repository files store only a policy reference, never the secret credential;
- publication may later move from restricted to public after explicit human authorization;
- changing reader visibility does not imply changing the source repository from private to public.

A currently shared reading credential may be used as a transitional operational policy, but its secret value must remain provider-side and outside Git, logs, issues, pull requests, and chat.

## 5. Required agent reconstruction report

Before material configuration or upgrade work, the agent should be able to state:

- which component it entered through;
- the four component roles and public entrypoints;
- the selected downstream profile;
- active, deferred, and not-applicable components;
- pinned upstream revisions;
- source privacy and Web visibility;
- publication authorization state;
- Cloudflare deployment profile and access policy;
- which actions are already authorized and which remain human-reserved;
- which provider state still needs verification.

If those facts cannot be reconstructed, treat the situation as a configuration defect rather than guessing.

## 6. Public-delivery migration rule

For the four public framework sites, Cloudflare Pages is the preferred delivery provider and GitHub remains the canonical source/version-control provider.

Until the migration plan reports a verified cutover:

- the existing GitHub Pages URLs remain the current public entrypoints;
- a `*.pages.dev` URL is staging, not the stable ecosystem identity;
- an agent must not rewrite public entry URLs merely because a Cloudflare project exists;
- the preferred stable identity is a verified custom domain;
- the migration state must be read from `templates/cloudflare-public-delivery.yaml`;
- the coordinated cutover must follow `docs/CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.md`.

If the migration has not reached the verified-cutover state, treat any proposed new public URL as provisional provider state.

## 7. Cloudflare human-handoff standard

When a Cloudflare action cannot be completed through an already authorized tool, the agent must not say only “configure Cloudflare” or “enable Access.” It must give numbered, operator-level instructions that include:

1. where to sign in and which account/project/domain is the target;
2. the exact Dashboard area or current UI path to open;
3. the value or setting to choose, while clearly marking any value that must come from the project contract;
4. which secrets must not be copied into chat;
5. the completion condition the human should observe;
6. what the agent will verify after the human completes the step;
7. the rollback path if the operation changes routing, publication, or access.

If the live provider UI differs from a recorded runbook, the agent must inspect current provider documentation or UI rather than inventing a path.

## 8. Canonical public entrypoints

- AHICP: https://chongliuphil.github.io/AI-Assisted-Human-Inquiry-and-Creation-Protocol/
- PPF: https://chongliuphil.github.io/Personal-Publishing-Framework/
- Vault Interface: https://chongliuphil.github.io/Vault-interface/
- Starter: https://chongliuphil.github.io/Inquiry-Publishing-Project-Starter/

Machine-readable ecosystem:
https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/blob/main/ecosystem.yaml

Continuous Web and Cloudflare guide:
https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/blob/main/docs/CONTINUOUS_WEB_CLOUDFLARE.md
