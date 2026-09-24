# Cloudflare minimal-human handoff

**Status:** canonical operator handoff for private/restricted Continuous Web  
**Default new-project infrastructure profile:** `agent-provisioned-external-ci`  
**Policy reference:** `shared-reader-access`

This guide reduces repeated human work by separating **platform bootstrap** from **project provisioning**.

For the full orchestration contract, read [PROJECT_PROVISIONING_CONTRACT.md](PROJECT_PROVISIONING_CONTRACT.md). PPF remains authoritative for the executable provider implementation.

## 1. Canonical access model

For unpublished/restricted work:

```text
restricted Worker hostname
-> Cloudflare Access
-> account-wide all_workers baseline
-> project/audience policy
-> authenticated reader
```

The access-policy reference may be stored in project files. Reader identities, application/policy IDs that are account-private, credentials, OTPs, and token values remain private provider state.

A generic shared static password is not the canonical model.

## 2. The minimum human role

For the preferred new-project profile, ordinary projects should not require a new Cloudflare ↔ GitHub authorization.

The human normally acts only at these boundaries:

### Platform bootstrap — one-time / infrequent

1. Sign in to Cloudflare and complete MFA.
2. Authorize a bounded Cloudflare provisioning principal.
3. Establish and verify an account-wide Access baseline covering `all_workers`.
4. Establish the trusted Secret Broker / token-minting boundary.
5. Authorize the GitHub provisioning principal for the intended GitHub owner/organization scope.

### Later human-reserved decisions

- public release;
- adding or expanding readers;
- a new custom/canonical domain or DNS authority;
- expanding GitHub or Cloudflare permission scope;
- paid-plan/billing changes;
- fallback direct secret entry if the trusted broker is unavailable.

Creating another private/restricted project inside already approved platform scopes is **not** itself a human gate.

## 3. Cloudflare provisioning principal

The platform principal needs only the capabilities required by the selected implementation, but new Worker creation is broader than routine deployment.

Current Cloudflare Workers roles distinguish:

- product-level **Admin** — can create Workers;
- individual-Worker **Editor** — can update/deploy an existing Worker but cannot delete it.

Therefore:

```text
platform provisioner
  -> Workers product Admin for creation

project CI
  -> individual Worker Editor for routine deployment
```

Do not give the project CI the platform provisioning credential.

## 4. High-privilege token-minting boundary

Automatically creating an account-owned API token is itself a high-privilege account operation.

Current Cloudflare account-token documentation requires elevated account authority to create/update account-owned tokens. This power belongs only inside the trusted Secret Broker / provisioning boundary.

The language model and project CI must never receive that minting authority.

The broker should create:

```text
account-owned API token
scope: specified individual Worker
role: Editor
```

and transfer it directly into the target repository's GitHub Actions secrets.

## 5. Secret Broker contract

The PPF provisioner returns only a non-secret `ppf/secret-broker-request/v1`.

The trusted broker performs atomically:

1. resolve the target Worker;
2. create the scoped account-owned Worker token;
3. obtain the repository Actions-secret public key / secure write interface;
4. write `CLOUDFLARE_API_TOKEN`;
5. write `CLOUDFLARE_ACCOUNT_ID`;
6. discard plaintext token material;
7. return only non-secret installation status and identifiers.

Never paste the token into chat, a PR, an issue, a repository file, or an Agent-visible log.

## 6. Account-wide Access bootstrap

Before automatic project Worker creation, verify an Access application whose destination covers `all_workers` or an equivalent account-wide baseline.

This baseline should protect existing and future Workers.

The project provisioner must fail closed if the baseline cannot be verified.

Public production later becomes an explicit exact-project exception; do not disable the baseline for the account.

## 7. Reader authentication

A reusable policy such as `shared-reader-access` may use an approved identity mechanism such as One-Time PIN and an explicit allowed audience.

Do not create a broad Everyone/all-email Allow rule merely to make authentication easy.

For each restricted project, verification must include:

- anonymous request challenged/denied;
- approved reader succeeds when an audience has actually been approved;
- unapproved reader fails;
- direct asset/feed/generated-file URLs cannot bypass Access.

Reader identities are private state and do not belong in the public project repository.

## 8. Agent execution after platform bootstrap

After platform authorization is recorded as ready, the Agent should normally:

1. validate `project-provisioning.yaml`;
2. verify that the requested GitHub owner is within scope;
3. re-verify account-wide Access;
4. invoke the pinned PPF provisioner;
5. create/reuse the private repository and restricted Worker;
6. pass the non-secret broker request to the trusted broker;
7. verify deployment-secret metadata without reading secret values;
8. run repository validation and authorized GitHub Actions deployment;
9. verify the exact deployed revision and restricted HTTP behavior;
10. persist only non-secret state and rollback evidence.

Stop before public release unless the human separately authorizes it.

## 9. Workers Builds Native alternative

`workers-builds-native` remains supported for projects that explicitly choose provider-native Git integration or already use it.

That path requires the Cloudflare Workers & Pages GitHub App and its repository authorization. Its build credential remains a user-token model rather than the preferred one-Worker account-owned deployment identity.

Do not mix the two profiles in one project without an explicit migration plan.

## 10. Completion gate

Restricted Continuous Web is complete only when:

- private GitHub source is correct;
- account-wide Access remains verified;
- target Worker is correct;
- project deployment secrets are installed without secret disclosure;
- repository/build checks pass;
- deployed revision matches the intended source;
- anonymous production access is challenged/denied;
- direct assets cannot bypass Access;
- enabled previews, if any, are independently protected;
- rollback is known;
- only non-secret provider state is written back.

Deployment success does not authorize public release.
