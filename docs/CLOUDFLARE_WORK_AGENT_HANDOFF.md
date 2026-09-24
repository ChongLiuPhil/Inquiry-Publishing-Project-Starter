# Cloudflare Work / browser-agent handoff prompt

Use this file as the task prompt for a browser-capable agent such as ChatGPT Work.

> Open the target Cloudflare account and configure the project's private Continuous Web according to the repository contracts. Read the Starter ecosystem, Agent Retrieval Contract, Project Provisioning Contract, Continuous Web/Cloudflare guide, Cloudflare minimal-human handoff, the project's publishing.yaml and cloudflare-builds.yaml, and the pinned PPF per-project setup guide before changing provider state.
>
> Default ordinary new projects to the personal ChongLiuPhil GitHub account, a private repository, workers-builds-native, Worker-scoped Cloudflare Access, and previews disabled. Do not require account-wide Project Provisioner infrastructure unless the project explicitly selected the advanced external-CI profile.
>
> Reconstruct and report the exact target Cloudflare account, Worker/project, GitHub repository, production branch, build/deploy commands, publication authorization state, intended Access mode/policy, and current repository connection before making changes.
>
> Perform every safe browser-operable step yourself. For the default profile, stop and ask the human only when account-holder interaction is actually required: GitHub/Cloudflare sign-in or MFA, repository-level Cloudflare Git authorization, selecting/approving reader identity policy, or a human-reserved publication/domain/billing decision. Never ask the human to paste a password, API token, private key, recovery code, or other secret into chat.
>
> Connect the target private repository to Workers Builds, keep non-production/preview builds disabled, verify the first deployment, protect the Worker with Access using All traffic unless verified account-wide protection already applies, and verify anonymous denial plus authenticated access.
>
> Then make or request one harmless source update and verify a second push automatically redeploys without renewed GitHub or Cloudflare authorization. The project is not operationally verified until this second-push check passes.
>
> Do not switch the restricted publication to public, make the repository public, expand readers, change DNS/custom domain authority, expand provider permissions, or enable a paid plan without explicit human authorization.
>
> Finish with a non-secret verification report containing actual provider IDs/URLs, source revision, repository-connection state, Access policy/application IDs, first-deployment and second-push PASS/FAIL results, rollback information, and any remaining human decision.
