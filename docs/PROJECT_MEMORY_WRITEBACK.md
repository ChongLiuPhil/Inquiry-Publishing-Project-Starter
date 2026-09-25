# Project Memory and Bootstrap Write-Back Contract

**Status:** canonical cross-component persistence rule for new projects  
**Principle:** repository state outranks chat, account memory, and Agent recollection.

This contract exists so that a new Agent can take over a project with zero access to the previous conversation and still reconstruct the current GitHub → Cloudflare setup state.

Nothing operationally important may exist only in an AI conversation.

## 1. Durable state layers

A full-stack project uses four complementary durable records:

1. **`project-provisioning.yaml` — intended configuration**
   - selected infrastructure profile;
   - intended GitHub owner/repository/privacy;
   - intended Cloudflare Worker/access mode;
   - publication authorization boundary.

2. **`project-bootstrap-state.yaml` — actual operational bootstrap state**
   - which human/provider steps are pending/completed/blocked;
   - current repository/Workers Builds/Access status;
   - first-deployment and second-push acceptance status;
   - non-secret evidence and rollback references.

3. **AHICP Working Memory — current work and resume point**
   - `docs/working-memory/current-focus.zh-CN.md`;
   - `docs/working-memory/task-plan.zh-CN.md`;
   - `docs/working-memory/work-log.zh-CN.md`.

4. **AHICP long-term memory / Decision Log — durable human decisions**
   - publication decisions;
   - scope/permission changes;
   - reader/audience policy decisions;
   - other decisions that change project policy rather than merely report provider state.

These roles must not be collapsed into one chat summary.

## 2. Write-before-handoff rule

Before asking the human to perform a GitHub or Cloudflare UI action, the Agent MUST write the pending step into durable project state.

At minimum:

- set the matching `project-bootstrap-state.yaml -> human_steps.<step>.status` to `waiting-human`;
- set project `status: waiting-human`;
- record the exact `guide_ref`;
- put the pending human action and exact resume condition into AHICP Task Plan;
- update Current Focus when this is the immediate blocker.

The human should never have to rely on scrolling back through chat to recover what to click next.

## 3. Write-after-human-action rule

After the human reports that a step is complete, the Agent MUST verify the resulting provider/repository state when tools permit.

Only after verification may it:

- mark the human step `completed` (or `not-required`);
- update the relevant GitHub / Cloudflare actual-state field;
- record non-secret completion evidence;
- update `last_updated`;
- update AHICP Task Plan and Current Focus;
- append a high-level milestone to Work Log when the bootstrap materially advances.

A human saying “done” is a cue to verify, not by itself sufficient proof of provider state.

## 4. Human UI instructions must be durable

Every human-required provider action must have a repository-backed operator guide containing:

- exact target account/repository/Worker;
- current dashboard navigation path;
- exact non-secret values to select or enter;
- what **not** to paste into chat;
- what success looks like in the UI;
- what the Agent will verify after the human returns;
- rollback / correction path.

For the default Workers Builds Native profile, the authoritative operator guide is the pinned PPF:

`docs/PER_PROJECT_GITHUB_CLOUDFLARE_SETUP.md`

Starter acceptance is:

`docs/PROJECT_PROVISIONING_ACCEPTANCE.md`

If provider UI changes, update the repository guide from current official Provider documentation before instructing the human. Do not keep a corrected procedure only in chat.

## 5. Default bootstrap state sequence

The normal `workers-builds-native` project moves through:

```text
not-started
-> waiting-human / repository creation if needed
-> repository private verified
-> Git account connection reused or created
-> repository access authorized if needed
-> Workers Builds connected
-> Worker name alignment verified
-> Zero Trust verified (or setup completed once)
-> Worker Access verified-private
-> first-deployment-verified
-> second-push-auto-deploy verified
-> operationally-verified
```

A failure at any stage is persisted as `blocked` with the next repair action in Task Plan.

## 6. Exact state ownership

| Fact | Durable authority |
| --- | --- |
| Intended deployment profile / privacy / access mode | `project-provisioning.yaml` |
| Actual repository / Workers Builds / Access / deployment status | `project-bootstrap-state.yaml` |
| Current blocker and next human/Agent action | AHICP Current Focus + Task Plan |
| Milestone history | AHICP Work Log |
| Durable human policy/publication decisions | AHICP Decision Log / appropriate Core |
| Secret values / tokens / OTP / recovery codes | **Never repository or chat** |

Provider dashboards remain the actual external system state; repository records store the last verified non-secret projection of that state.

## 7. Secret boundary

The bootstrap-state file may store:

- repository URL;
- Worker URL;
- non-secret provider IDs;
- source revisions;
- verification result;
- Access application reference;
- rollback/version reference.

It must not store:

- passwords;
- API token values;
- OAuth codes;
- private keys;
- OTPs;
- recovery codes;
- reader credentials;
- session cookies.

The schema hard-codes `secret_material: forbidden`.

## 8. Onboarding requirement

A replacement Agent must not reconstruct infrastructure state from prior chat.

For a full-stack project, after the normal AHICP Working Memory read, it should read:

- `project-stack.yaml`;
- `project-provisioning.yaml`;
- `project-bootstrap-state.yaml`;
- the pinned PPF per-project operator guide when provider work is in scope.

If these records disagree with provider actual state, record a synchronization defect and reconcile before further mutating work.

## 9. Completion requirement

A project cannot be described as operationally verified until:

- `project-bootstrap-state.yaml.status == operationally-verified`;
- repository privacy is verified;
- Workers Builds repository connection is verified;
- Worker name alignment is verified;
- Access is verified private;
- first deployment is verified;
- second push automatically deploys without renewed authorization;
- memory write-back is synchronized;
- public release remains not authorized unless a later explicit human decision changes it.

The completion state belongs in the repository, not in the Agent's memory.
