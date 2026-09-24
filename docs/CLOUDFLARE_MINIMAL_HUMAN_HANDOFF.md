# Cloudflare minimal-human handoff

**Status:** canonical operator handoff for the default per-project private/restricted Continuous Web setup  
**Default new-project infrastructure profile:** `workers-builds-native`  
**Default setup mode:** `human-assisted-once-per-project`

This guide defines the smallest practical human role for an ordinary new project.

The goal is no longer “authorize the whole account once and never touch another project.” The goal is:

> **one short project bootstrap, then automatic deployment on ordinary pushes.**

For the full orchestration contract, read [PROJECT_PROVISIONING_CONTRACT.md](PROJECT_PROVISIONING_CONTRACT.md). PPF remains authoritative for the executable provider implementation.

## 1. Default project model

```text
private GitHub repository under ChongLiuPhil
-> one Cloudflare Git repository connection
-> Workers Builds
-> Worker-scoped Cloudflare Access
-> first restricted deployment
-> second push verifies automatic redeployment
```

Account-wide Access and account-wide provisioning automation are optional optimizations, not prerequisites.

## 2. The normal human role

For each new project, the human may need to:

1. create or confirm the private GitHub repository;
2. approve Cloudflare Git access to that repository if GitHub asks;
3. select/connect the repository in Cloudflare Workers & Pages;
4. confirm the production branch/build settings;
5. enable Worker-scoped Cloudflare Access and select the approved authentication policy;
6. confirm the first restricted deployment.

These are accepted per-project consent steps.

The Agent should perform every independent technical step it can before and after them.

## 3. Exact default values

Use the pinned project/PPF contracts as source of truth.

Ordinary reference values:

```text
GitHub owner: ChongLiuPhil
repository visibility: private
production branch: main
Cloudflare profile: workers-builds-native
root directory: /
build command: bash scripts/cloudflare_build.sh
deploy command: npx wrangler deploy
preview/non-production builds: disabled
Access mode: worker-scoped-access
public release: not authorized
```

If current provider UI differs, verify current official documentation and actual provider state rather than guessing.

## 4. Repository connection

In Cloudflare Workers & Pages:

1. choose **Create application** / repository import;
2. select the intended GitHub repository;
3. if the repository is missing, manage the Cloudflare GitHub App installation and grant access to this repository;
4. configure the pinned build/deploy values;
5. save/deploy.

Prefer repository-scoped GitHub App access where practical.

No Cloudflare deployment token should be pasted into chat for this default profile.

## 5. Worker Access

After the Worker exists:

1. open the Worker;
2. open **Access**;
3. choose **Protect this Worker behind Access**;
4. choose **All traffic**;
5. select/create the approved authentication policy;
6. apply the policy.

If verified account-wide **Protect all Workers** already covers the target Worker, record that actual mode instead of duplicating policy.

Do not claim private readiness until an anonymous request is challenged or denied.

## 6. First-deployment verification

Verify:

- repository remains private;
- Cloudflare points to the intended repository;
- production branch is `main`;
- deployed source revision is correct;
- anonymous production access is denied/challenged;
- approved authenticated access works;
- direct asset URLs do not bypass Access;
- no secret value appears in Git/chat/logs.

## 7. Second-push verification

Make a harmless source change and push it to `main`.

Pass only if:

```text
push
-> Workers Builds starts automatically
-> new revision deploys
-> Access remains active
-> no renewed GitHub or Cloudflare authorization is required
```

This is the evidence that the per-project bootstrap is complete.

## 8. Human-reserved decisions

Always return to the human for:

- public Web release;
- making the source repository public;
- reader-audience expansion;
- custom domain or DNS changes;
- provider-permission expansion;
- paid-plan or billing changes.

## 9. Optional advanced profile

If the project explicitly selects `agent-provisioned-external-ci`, follow the advanced PPF runbooks instead. That path uses platform authorization, GitHub Actions, an individual-Worker `Editor` token, and the Trusted Secret Broker.

Never mix the two profiles without an explicit migration plan.

## 10. Completion gate

The default setup is complete only when:

- private source identity is correct;
- Workers Builds repository connection is verified;
- target Worker is correct;
- Access is verified private;
- first restricted deployment is verified;
- second push auto-deploys without reauthorization;
- rollback/restore is known;
- only non-secret provider state is written back;
- public release remains unauthorized.
