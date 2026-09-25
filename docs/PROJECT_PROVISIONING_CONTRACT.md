# Project Provisioning Contract

**Status:** canonical Starter orchestration contract  
**Default infrastructure profile:** `workers-builds-native`  
**Default setup mode:** `human-assisted-once-per-project`  
**Default CI cost profile:** `private-project-quota-saver`

This contract defines the practical new-project path for the Inquiry Publishing Stack.

The default no longer assumes account-wide zero-touch provisioning. A small amount of human GitHub/Cloudflare configuration is explicitly allowed once for each project. After that project bootstrap, ordinary source pushes should deploy automatically.

The advanced `agent-provisioned-external-ci` + Trusted Secret Broker route remains available when a project explicitly selects it.

## 1. Default goal

For an ordinary new project, the target flow is:

```text
human project request
-> private repository under ChongLiuPhil
-> full AHICP + full PPF + Vault Interface adoption
-> project infrastructure manifest
-> one-time Cloudflare Git repository connection
-> Workers Builds
-> Worker-scoped Cloudflare Access
-> first restricted deployment verification
-> second push without reauthorization
-> ordinary future pushes deploy automatically
```

The practical promise is:

> **one short, documented project bootstrap; then automatic deployment on ordinary pushes.**

It is not a claim that every future repository can be created and connected without human interaction.

## 2. Default GitHub topology

Ordinary downstream projects default to:

```yaml
github:
  owner: ChongLiuPhil
  owner_type: user
  visibility: private
```

The repository may be created manually in GitHub before the Agent configures it. Automatic repository creation is an optimization, not a prerequisite.

The default path therefore does not require a GitHub Organization or a platform-wide Project Provisioner App.

The repository must start private. Making it public is a separate human-reserved decision.

## 3. Default Cloudflare topology

The default PPF infrastructure profile and CI cost profile are:

```text
workers-builds-native
private-project-quota-saver
```

The project connects its private GitHub repository to Cloudflare Workers Builds. Cloudflare then owns the Git-triggered build/deploy connection and provider-managed build credential.

Reference project settings:

```text
Worker/application name: exactly wrangler.jsonc.name
production branch: main
root directory: /
build command: bash scripts/cloudflare_build.sh
deploy command: npx wrangler deploy
preview / non-production builds: disabled by default
```

If the Git account is already connected to Cloudflare, reuse that account connection. A new project should not repeat OAuth merely because it is new. If the private repository is not visible, authorize or expand the Cloudflare GitHub App's access only for the target repository where practical.

The exact provider UI may change. The Agent must follow current provider state and the pinned PPF setup contract rather than guessing from stale screenshots.

### Private-project CI cost default

The pinned PPF `private-project-quota-saver` policy is part of the default project state:

- content-only changes do not start GitHub Actions;
- configuration/infrastructure pull requests targeting `main` use one lightweight contract check only;
- pushes to `main` do not run a duplicate GitHub Actions Web build;
- full Web validation, Cloudflare contract validation, publication artifacts, and advanced external deployment are manual;
- automatic success artifacts are not uploaded, and manual publication artifacts default to one-day retention;
- Cloudflare Workers Builds owns the only automatic production Web build;
- non-production Cloudflare builds and previews remain disabled by default.

The Agent must batch related edits, run all available Agent-side preflight checks, inspect the complete diff, and then trigger only the intended thin CI. GitHub Actions must not be used as the iterative debugging loop. If the private-repository Actions quota is exhausted, optional/manual GitHub heavy validation stays deferred unless the human explicitly authorizes paid usage.

CI/cost profiles are intentionally layered: ordinary private projects use `private-project-quota-saver`; hardened `agent-provisioned-external-ci` projects use `external-ci-required`; public framework repositories use `full-validation` as the machine-readable full-CI profile.

## 4. One-time human project bootstrap

The normal human bootstrap may include:

1. create or confirm the private personal-account GitHub repository;
2. reuse the existing Cloudflare Git-account connection when it already works;
3. if the target private repository is not visible, authorize or expand the Cloudflare GitHub App's repository access for that repository;
4. connect the repository to Workers Builds and set the Worker/application name to exactly match `wrangler.jsonc.name`;
5. confirm the intended production branch/build settings;
6. if Cloudflare Zero Trust has never been enabled on the account, complete that one-time account prerequisite; later projects reuse it;
7. protect the target Worker with Cloudflare Access, preferably reusing an already-approved authentication policy;
8. confirm the first restricted deployment.

These steps are project-level authorization, not a failure of the system.

The Agent should do every independent technical step it can, and return to the human only for the provider UI/consent steps that actually require the account holder.

## 5. Private Web default

New unpublished Web output defaults to:

```text
restricted + authenticated
```

The normal Access mode is:

```text
worker-scoped-access
```

If an account-wide `all_workers` policy is already enabled and verified, a project may record:

```text
account-wide-access
```

instead.

A project must not be called private merely because the GitHub repository is private. The Worker itself must be protected, and anonymous access must actually be challenged or denied.

Preview deployments remain disabled by default until their protection is separately verified.

## 6. Project request

A new project uses:

- `schema/project-provisioning-request.schema.json`
- `templates/project-provisioning-request.yaml`
- root `project-provisioning.yaml`

The default request declares:

- `full-research-publication`;
- GitHub owner `ChongLiuPhil`;
- `owner_type: user`;
- private repository;
- `workers-builds-native`;
- `ci_cost_profile: private-project-quota-saver`;
- `access_mode: worker-scoped-access`;
- restricted Web;
- previews disabled;
- no custom domain;
- `restricted_deployment_source: explicit-project-authorization`;
- `project_bootstrap: human-assisted-once-per-project`;
- `public_release: false`.

The request contains no credential material.

## 7. Planner semantics

For the default Native profile, an unconfigured platform-authorization record does **not** block project planning.

The default ready state is:

```text
READY_FOR_PROJECT_BOOTSTRAP
```

The generated PPF desired state uses:

```text
provider: cloudflare-workers-builds
securityProfile: workers-builds-native
credentialStrategy: provider-managed-user-token
secretBroker: false
ciCostProfile: private-project-quota-saver
accessMode: worker-scoped-access
previewDeployments: false
```

Platform standing authorization is required only if the project explicitly selects the advanced External-CI profile.

## 8. Verification after first setup

The first deployment is not sufficient on its own.

Verify:

- the GitHub repository remains private;
- Cloudflare is connected to the intended repository;
- the production branch is `main`;
- the intended revision is deployed;
- Worker Access protection is active;
- anonymous production requests are challenged or denied;
- an approved authenticated reader can access the site;
- direct assets cannot bypass Access;
- no provider credential value appears in Git, issues, PR text, logs, or model/chat context.

Record only non-secret provider state.

## 9. Second-push acceptance

After the first deployment succeeds, make one harmless source change and push it to `main`.

The project is operationally verified only if:

```text
push
-> Workers Builds starts automatically
-> build succeeds
-> intended new revision deploys
-> Access remains enforced
-> no duplicate GitHub Actions production Web build starts
-> no renewed GitHub or Cloudflare authorization is required
```

This is the important evidence that the one-time project bootstrap has actually become a reusable connection.

## 10. Human-reserved gates

The default project bootstrap never authorizes:

- Web publication becoming public;
- source repository becoming public/open source;
- reader-audience expansion;
- custom-domain or DNS changes;
- provider-permission scope expansion;
- paid-plan or billing changes;
- enabling paid GitHub Actions usage, increasing an Actions budget, or otherwise changing billing to bypass the quota.

Those remain explicit human decisions.

## 11. Secret boundary

For the default Native profile, the user is not asked to copy a Cloudflare deployment token into GitHub Actions or chat. Workers Builds uses provider-managed credentials.

No provider credential may be stored in:

- Git;
- Starter/PPF YAML;
- issues or PR bodies;
- logs;
- chat/model context.

If API-based automation is later used for provider configuration, credentials must remain inside an authorized provider/tool boundary.

## 12. Optional advanced External-CI profile

A project may explicitly select:

```text
agent-provisioned-external-ci
```

when stronger deployment-credential isolation is worth the additional infrastructure.

That profile retains:

- reusable platform authorization;
- account-wide Access precondition;
- GitHub Actions deployment;
- account-owned individual-Worker `Editor` credential;
- Trusted Secret Broker orchestration.

Its Cloudflare granular-token issuer remains subject to live Provider acceptance. The advanced profile must not be used to make claims about the default Native path.

## 13. Completion state

A default project bootstrap is complete when it can truthfully record:

```text
github_repository: private
infrastructure_profile: workers-builds-native
ci_cost_profile: private-project-quota-saver
cloudflare_git_connection: verified
worker_access: verified-private
first_restricted_deployment: verified
second_push_auto_deploy: verified
public_release: NOT AUTHORIZED
```

Starter owns composition and project-bootstrap orchestration. PPF remains authoritative for the executable GitHub/Cloudflare integration contract and operator instructions.
