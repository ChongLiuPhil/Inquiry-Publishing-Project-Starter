# Project Provisioning Contract

**Status:** canonical Starter orchestration contract  
**Preferred infrastructure profile:** `agent-provisioned-external-ci`

This contract defines how the Inquiry Publishing Stack turns a new project request into an adopted, private-by-default, deployable project while minimizing repeated human authorization.

Starter owns **composition and provisioning intent**. It does not duplicate provider implementation. PPF remains authoritative for executable GitHub/Cloudflare infrastructure adapters, reconciliation, deployment profiles, and verification.

## 1. Goal

After platform bootstrap, the ordinary new-project path should be:

```text
human project request
-> Starter validates platform standing authorization
-> private GitHub repository
-> full AHICP + full PPF + Vault Interface adoption
-> PPF project infrastructure manifest
-> account-wide Access precondition
-> Cloudflare Worker
-> trusted secret broker
-> GitHub Actions restricted deployment
-> live verification
-> durable non-secret write-back
```

The human should not be asked to repeat provider authorization merely because another project is created inside already approved GitHub and Cloudflare scopes.

## 2. No second infrastructure control plane

Starter does not implement Cloudflare or GitHub provisioning APIs.

The executable provider authority is the PPF infrastructure layer:

- `providers/infrastructure/provisioning.py`
- `providers/infrastructure/coordinator.py`
- `schema/project.infrastructure.schema.json`
- `docs/AGENT_PROVISIONED_EXTERNAL_CI.md`
- `docs/TRUSTED_SECRET_BROKER.md`

Starter is responsible for selecting the PPF profile, creating the project-level request, checking platform authorization, applying the stack template, and preserving the human decision boundary.

## 3. Platform authorization

The reusable non-secret authorization state is represented by:

- `schema/platform-authorization.schema.json`
- `templates/platform-authorization.yaml`

Platform authorization records only references and verified states. It must never contain API tokens, private keys, passwords, recovery codes, OTPs, or reader identities.

A platform is `ready` only after all of these are verified:

### GitHub

- approved owner/organization scope;
- provisioning principal authorized for that scope.

### Cloudflare

- provisioning principal authorized;
- account-wide `all_workers` Access baseline verified;
- Worker creation authority verified;
- account-owned token minting authority is isolated inside the trusted Secret Broker / provisioning boundary and that isolation is verified.

### Secret broker

- a trusted broker implementation exists and has been verified to transfer a project deployment credential into GitHub Actions without exposing plaintext to the Agent/model.

## 4. Standing authorization

Platform authorization may include standing approval for low-risk, private-by-default project setup:

```yaml
standing_authorizations:
  create_private_repositories: true
  create_restricted_workers: true
  restricted_web_deployment: true
  public_release: false
  source_repository_public: false
  reader_audience_expansion: false
  custom_domain_change: false
  provider_permission_scope_expansion: false
  paid_plan_change: false
  direct_secret_input: false
```

For the current platform topology, the approved GitHub scope is intended to be the `philohub` Organization. Once the Project Provisioner App installation for that Organization is verified, a later project does not need another human confirmation for:

- creating its private repository under `philohub`;
- creating a Worker protected by the verified account-wide Access baseline;
- deploying a restricted/authenticated Continuous Web publication;
- verifying that deployment.

It does **not** authorize:

- making the publication public;
- publishing/open-sourcing the source repository;
- adding or expanding readers;
- selecting a new custom domain or changing DNS;
- expanding provider permission scope;
- enabling a paid plan.

## 5. Project request

A new project request uses:

- `schema/project-provisioning-request.schema.json`
- `templates/project-provisioning-request.yaml`

The default request declares:

- `full-research-publication`;
- GitHub owner `philohub` with `owner_type: organization`;
- private GitHub source;
- `agent-provisioned-external-ci`;
- restricted Web;
- previews disabled;
- `shared-reader-access`;
- no custom domain;
- no public-release authorization.

The request contains no credential material.

## 6. Project composition

For the default full profile, Starter adopts:

```text
full AHICP
+ full PPF
+ Vault Interface
+ project-owned content
```

The Agent must still fresh-read the pinned upstream ownership manifests before writing project files.

For PPF, the preferred new-project infrastructure profile is `agent-provisioned-external-ci`. Workers Builds Native remains available only after an explicit profile selection or for an existing project that already uses it.

## 7. Restricted deployment standing policy

If `standing_authorizations.restricted_web_deployment` is true and the request uses `restricted_deployment_source: platform-standing-authorization`, Starter may materialize the downstream PPF project so that restricted Continuous Web deployment is authorized without a new project-by-project approval.

That authorization is limited to the declared restricted/authenticated state.

It must **not** set or imply:

- `visibility: public`;
- public Access bypass;
- source repository public;
- custom domain authorization;
- reader-audience expansion;
- public canonical cutover.

Public release still needs a separate durable approval.

## 8. Provisioning sequence

An Agent should execute the following sequence:

1. Read Starter ecosystem and retrieval contract.
2. Read this contract.
3. Validate the platform authorization record.
4. Validate the project provisioning request.
5. Resolve the full Starter profile and pinned upstream sources.
6. Create/adopt project files in the private repository.
7. Fresh-read PPF's provisioning profile and infrastructure schema.
8. Invoke the PPF provisioner.
9. If PPF returns `SECRET_BROKER_REQUIRED`, send only that non-secret request to the trusted broker.
10. Re-read GitHub secret metadata; never read the secret value.
11. Materialize restricted deployment authorization only when covered by standing or explicit project authorization.
12. Run CI/deployment.
13. Verify repository privacy, account-wide Access, deployed revision, anonymous denial, assets, and rollback.
14. Write non-secret IDs/status and verification evidence back to private project state.
15. Stop before any human-reserved gate.

## 9. Human-reserved gates

The Agent returns to the human only when the requested action is outside the standing platform/project authorization, including:

- GitHub provisioning scope expansion;
- Cloudflare provisioning scope expansion;
- missing account-wide Access bootstrap;
- missing trusted secret broker requiring direct secret input;
- reader-audience addition or expansion;
- public publication;
- source repository public/open-source transition;
- custom domain / DNS authority;
- paid-plan change.

A human gate is a resumable checkpoint. The Agent continues all other independent authorized work and resumes from fresh provider state after the gate is completed.

## 10. Secret boundary

Secrets never belong in:

- Starter templates;
- `project-stack.yaml`;
- the provisioning request;
- platform authorization YAML;
- issues or PR bodies;
- logs;
- chat/model context.

The PPF provisioner returns only a non-secret `ppf/secret-broker-request/v1`.

PPF now implements the atomic Secret Broker orchestration and safe `ppf/secret-broker-result/v1` contract. It refuses to overwrite existing target Secrets, verifies the issuer-reported Worker/role scope, rolls back transaction-created Secrets, and revokes a newly minted token when the broker transaction fails. The Cloudflare granular-token issuer adapter remains `live-acceptance-pending` until the exact current individual-Worker `Editor` policy encoding is verified against the live Provider API.

The secret broker is a trusted execution boundary, not an LLM prompt. Starter must not treat “broker orchestration implemented” as equivalent to “Cloudflare token issuer production-accepted”.

## 11. Completion criteria

A project may be reported as **restricted-deployment verified** only when:

- the intended private GitHub repository exists;
- full-stack adoption state is recorded;
- the intended Worker exists;
- the account-wide Access baseline remains verified;
- project deployment credential metadata is installed;
- the intended Git revision is deployed;
- anonymous production access is challenged/denied;
- enabled previews, if any, are challenged/denied;
- direct assets cannot bypass Access;
- no secret value is present in Git/chat/logs;
- rollback is recorded;
- provider state has been written back without credential material.

It must still report:

`public_release: NOT AUTHORIZED`

until explicit human approval exists.

## 12. Evidence boundary

The contract, schemas, planner, PPF provisioner, workflow, and CI can establish implementation readiness.

They cannot establish live production acceptance for this new profile.

The first production-grade acceptance must use one clean test project, first record non-secret Provider evidence proving the minted Cloudflare credential is scoped to exactly the intended existing Worker with `Editor`, and then record:

```text
project request
-> private repo
-> stack adoption
-> Worker
-> secret broker
-> GitHub Actions deploy
-> restricted anonymous denial
-> revision verification
-> durable write-back
```

Only after that evidence exists should Starter describe the path as a verified automatic default.
