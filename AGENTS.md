# Agent contract

Before configuring, adopting, upgrading, publishing, or operating a project, read:

1. docs/ECOSYSTEM.md
2. ecosystem.yaml
3. docs/AGENT_RETRIEVAL_CONTRACT.md
4. docs/AI_ADOPTION_WORKFLOW.md
5. docs/PROJECT_PROVISIONING_CONTRACT.md for every new project or when project infrastructure provisioning is in scope
6. docs/CONTINUOUS_WEB_CLOUDFLARE.md whenever Continuous Web or Cloudflare is in scope
7. docs/CLOUDFLARE_MINIMAL_HUMAN_HANDOFF.md when a human/account-owner action is required
8. docs/CLOUDFLARE_WORK_AGENT_HANDOFF.md when a browser-capable agent is executing provider UI work

The default new-project baseline is **full AHICP + full PPF + Vault Interface + project-owned content**. Use the full-research-publication profile unless the human explicitly selects a reduced profile. After platform bootstrap, prefer `agent-provisioned-external-ci` for infrastructure provisioning. Do not silently omit a component or repeatedly request account-level authorization when verified standing authorization already covers creation of another private/restricted project.

Original unpublished content, credentials, private working memory, and private control-plane state remain outside public repositories. For original work, the source repository is private by default. Continuous Web may still be enabled, but unpublished or transitional Web output is restricted by default and uses an access-policy reference rather than a secret stored in Git.

From any public component entrypoint, reconstruct the four-component ecosystem before cross-component configuration. Public links authorize retrieval of public information only; they do not authorize private-state access.

Before any Cloudflare operation, explain the exact target, affected layer, data flow, credential scope, human approval boundary, verification checks, and rollback. Project deployment credentials in the preferred profile must move through a trusted Secret Broker; the model must never receive token plaintext. When human UI interaction is required, provide numbered operator-level steps rather than a generic instruction. Never request passwords, tokens, private keys, recovery codes, or other secrets in chat.

Preserve proposal, authorization, execution, verification, and durable write-back as distinct stages.
