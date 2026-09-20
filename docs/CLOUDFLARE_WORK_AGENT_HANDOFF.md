# Cloudflare Work / browser-agent handoff prompt

Use this file as the task prompt for a browser-capable agent such as ChatGPT Work.

> Open the target Cloudflare account and configure the project's private Continuous Web according to the repository contracts. Read the Starter ecosystem, Agent Retrieval Contract, Continuous Web/Cloudflare guide, Cloudflare minimal-human handoff, the project's publishing.yaml and cloudflare-builds.yaml, and the current PPF provider runbooks before changing provider state.
>
> Reconstruct and report the exact target Cloudflare account, Worker/project, GitHub repository, production branch, build/deploy/preview commands, hostname, publication authorization state, and intended Access policy before making changes.
>
> Default original/unpublished source to private. Protect the Web publication with the reusable policy reference shared-reader-access. Prefer Cloudflare Access identity authentication with explicit approved reader emails and One-Time PIN; do not invent or request a static password.
>
> Perform every routine browser/API-operable step yourself. Stop and ask the human to take over only for Cloudflare sign-in/MFA, first GitHub App authorization, creation/capture of an API-token secret, approval of reader identities, direct entry of any pre-existing legacy secret, or final public-release approval. Never ask the human to paste a secret into chat.
>
> After each human-reserved step, resume automatically. Configure/verify Access, Workers Builds, preview deployment, hostname protection, direct assets/feeds, and rollback. Do not switch restricted publication to public without explicit human authorization.
>
> Finish with a non-secret verification report containing actual provider IDs, URLs, source revision, Access policy/application IDs, pass/fail checks, and any remaining human decision.
