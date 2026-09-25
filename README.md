# Inquiry Publishing Project Starter


[中文](README.zh-CN.md)

**New to the full stack?** Start with the [AHICP homepage](https://inquirystack.philohub.workers.dev/), which explains the system from the user’s point of view and provides a bootstrap instruction for AI setup.

**Project links:** [Public homepage](https://inquirystack.philohub.workers.dev/starter/) · [GitHub repository](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter)

**Related public projects:** [AHICP homepage](https://inquirystack.philohub.workers.dev/) · [PPF homepage](https://inquirystack.philohub.workers.dev/ppf/) · [Vault Interface homepage](https://inquirystack.philohub.workers.dev/vault-interface/)

**Machine entrypoint:** [Public agent landing](https://inquirystack.philohub.workers.dev/agent/) · [machine descriptor](https://inquirystack.philohub.workers.dev/agent/entry.json)

**Ecosystem and agent entrypoint:** [`docs/ECOSYSTEM.md`](docs/ECOSYSTEM.md) · [`ecosystem.yaml`](ecosystem.yaml) · [`Agent retrieval contract`](docs/AGENT_RETRIEVAL_CONTRACT.md) · [`Project Provisioning Contract`](docs/PROJECT_PROVISIONING_CONTRACT.md) · [`llms.txt`](docs/llms.txt) · [`Cloudflare guide`](docs/CONTINUOUS_WEB_CLOUDFLARE.md)


This repository is the **composition, adoption, upgrade, and project-provisioning orchestration layer** for three independent upstream systems:


- [AI-Assisted Human Inquiry and Creation Protocol (AHICP)](https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol)
- [Personal Publishing Framework (PPF)](https://github.com/ChongLiuPhil/Personal-Publishing-Framework)
- [Vault Interface](https://github.com/ChongLiuPhil/Vault-interface)


Starter is **not a fourth framework**. AHICP, PPF, and Vault Interface remain authoritative for their own specifications; Starter records how a project composes and adopts them, and when an authorized Agent may invoke the pinned PPF infrastructure provisioner.

**Default for new projects:** full AHICP + full PPF + Vault Interface. Downstream repositories default to the personal `ChongLiuPhil` GitHub account with `owner_type: user` and `visibility: private`; original or unpublished source remains private. The default infrastructure profile is `workers-builds-native`: allow one short human-assisted GitHub → Cloudflare bootstrap for the project, protect the Worker with Access, then verify that a second push deploys automatically without renewed authorization. `agent-provisioned-external-ci` remains an optional advanced profile. Public release remains a separate human decision. Reduced stack profiles require explicit human selection.


## Stack v2


Stack v2 keeps three easily confused facts separate:


- `template_source_commit`: the pinned upstream template/manifest revision used for composition and upgrade mechanics;
- `project_adopted_commit`: the semantic framework revision actually adopted by the project, when applicable;
- `adoption_state`: `active`, `deferred`, or `not-applicable`.


This lets existing projects reuse reliable structures, defer components when appropriate, and distinguish the template used for an upgrade from the framework revision the project actually accepted.


## Profiles


- `full-research-publication`: all three active — **default for new projects**
- `research-only`: Vault Interface + AHICP — explicit reduced-profile selection required
- `publishing-only`: Vault Interface + PPF — explicit reduced-profile selection required
- `research-book`: Vault Interface + AHICP, with PPF optional — explicit reduced-profile selection required


A profile describes composition, not project value.


## Machine-readable adoption


```bash
python -m pip install -r requirements-validation.txt
make stack-check
make stack-test
make upstream-check
make adoption-plan
make provisioning-contract-check
```


For machine-oriented output:


```bash
python tools/stack.py adoption-plan --json
```


The adoption plan reports active/deferred component state, authoritative repository, pinned template revision, the exact upstream manifest that owns upgrade classification, and the selected provisioning profile when present.

## Project provisioning

New downstream projects also carry `project-provisioning.yaml`. The public schemas/templates define only non-secret intent. The default `workers-builds-native` path does not require platform standing authorization; private platform-authorization state is consulted only when an optional advanced profile relies on it.

```bash
python tools/project_provisioning.py validate
python tools/project_provisioning.py plan --request project-provisioning.yaml --json
```

For the default `workers-builds-native` profile, the plan returns `READY_FOR_PROJECT_BOOTSTRAP` without requiring account-wide platform authorization. Follow the pinned PPF per-project setup guide to connect the private repository to Workers Builds, protect the Worker with Access, verify the first restricted deployment, and then verify a second push without reauthorization. The Secret Broker is required only by the optional advanced external-CI profile.

See [`docs/PROJECT_PROVISIONING_CONTRACT.md`](docs/PROJECT_PROVISIONING_CONTRACT.md) and [`docs/PROJECT_PROVISIONING_ACCEPTANCE.md`](docs/PROJECT_PROVISIONING_ACCEPTANCE.md).


## Upgrade safety


Starter does **not** copy AHICP or PPF ownership lists. For each active component, an agent must fresh-read the component manifest at its pinned `template_source_commit`. That upstream manifest is authoritative for `upstream-managed`, `merge-managed`, and `project-owned` paths.
