# Continuous Web and Cloudflare operational guide

This guide is a reusable operational contract, not a claim that every project has already been deployed.

## 1. Separate the four layers

```text
private source repository
    -> validation and build
    -> Cloudflare deployment
    -> reader-access policy
```

Keep these decisions separate:

- Source privacy: whether the canonical source and original work are private.
- Deployment identity: which credential may build or deploy.
- Reader access: who may read the deployed web output.
- Search visibility: whether crawlers may index the output.

Changing one layer must not silently change the others.

## 2. Default private-project posture

For unpublished or copyright-bearing work:

1. Keep the canonical repository private.
2. Use a private CI or Cloudflare-side Git integration; do not copy source into a public repository.
3. Deploy only the intended rendered output.
4. Put reader authentication in Cloudflare Access or an equivalent server-side gate.
5. Disable indexing for restricted material and verify that previews, assets, feeds, and generated files follow the same access policy.
6. Never commit passwords, API tokens, access policies containing secrets, or recovery codes.

A single reader password may be a temporary migration policy, but it is a shared secret. Prefer one centrally managed access policy with short-lived or individually revocable credentials when the project becomes sensitive or multi-user.

## 3. Deployment profiles

Choose and record one profile before deployment:

- **Native provider integration**: simplest operational path; validate the provider-managed credential scope and do not describe it as least privilege unless verified.
- **Hardened external CI**: GitHub Actions or another CI uses an account-owned token restricted to the target Worker or project; keep the token only in the CI secret store.
- **Future/provider-specific profile**: use only after the current provider documentation and a real test confirm its capability.

PPF's existing security profile documents provide the reference trade-offs. Deployment credentials and reader access remain orthogonal.

## 4. Required setup sequence

1. Define the project source repository, output directory, canonical domain, visibility, and retention policy.
2. Select the build and deployment profile.
3. Create or connect the Cloudflare project without exposing secrets to the repository.
4. Configure build commands and output paths from repository files.
5. Configure the custom domain only with the temporary authority needed for provisioning.
6. Configure reader access before exposing an unpublished output.
7. Run a preview build and verify HTML, assets, feeds, redirects, headers, and access behavior.
8. Run the production deployment only after the human approves the publication state.
9. Record the actual provider state, deployment revision, access policy, and verification result in private project state.
10. Keep a rollback path: prior build artifact or prior known-good commit, access-policy rollback, and domain-routing rollback.

## 5. AI-agent requirements

Before any Cloudflare action, the agent must provide:

- the exact target account/project/domain;
- whether the action changes deployment, DNS, routing, access, or only inspection;
- the credential type and least-privilege scope;
- where the human must authenticate or approve;
- what data is transmitted and what remains private;
- the preview and production verification checks;
- the rollback procedure and completion evidence.

The agent must not request that a human paste a password, API token, private key, or recovery code into chat. If a browser or provider UI requires such input, the human performs that step directly.

## 6. Completion gate

A Continuous Web setup is complete only when the repository build passes, the deployed URL is reachable under the intended policy, restricted content is not anonymously readable, public content is not accidentally restricted, and the verified provider state has been written back to the private project record.
