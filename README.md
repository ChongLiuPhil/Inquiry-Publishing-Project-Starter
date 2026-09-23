# Inquiry Publishing Project Starter


[中文](README.zh-CN.md)

**New to the full stack?** Start with the [AHICP homepage](https://inquirystack.philohub.workers.dev/), which explains the system from the user’s point of view and provides a bootstrap instruction for AI setup.

**Project links:** [Public homepage](https://inquirystack.philohub.workers.dev/starter/) · [GitHub repository](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter)

**Related public projects:** [AHICP homepage](https://inquirystack.philohub.workers.dev/) · [PPF homepage](https://inquirystack.philohub.workers.dev/ppf/) · [Vault Interface homepage](https://inquirystack.philohub.workers.dev/vault-interface/)

**Machine entrypoint:** [Public agent landing](https://inquirystack.philohub.workers.dev/agent/) · [machine descriptor](https://inquirystack.philohub.workers.dev/agent/entry.json)

**Ecosystem and agent entrypoint:** [`docs/ECOSYSTEM.md`](docs/ECOSYSTEM.md) · [`ecosystem.yaml`](ecosystem.yaml) · [`Agent retrieval contract`](docs/AGENT_RETRIEVAL_CONTRACT.md) · [`llms.txt`](docs/llms.txt) · [`Cloudflare guide`](docs/CONTINUOUS_WEB_CLOUDFLARE.md)


This repository is the **composition, adoption, and upgrade layer** for three independent upstream systems:


- [AI-Assisted Human Inquiry and Creation Protocol (AHICP)](https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol)
- [Personal Publishing Framework (PPF)](https://github.com/ChongLiuPhil/Personal-Publishing-Framework)
- [Vault Interface](https://github.com/ChongLiuPhil/Vault-interface)


Starter is **not a fourth framework**. AHICP, PPF, and Vault Interface remain authoritative for their own specifications; Starter records how a project composes and adopts them.

**Default for new projects:** full AHICP + full PPF + Vault Interface. Original or unpublished source is private by default; Continuous Web may still be prepared, but remains restricted and authenticated until explicit human public-release authorization. Reduced profiles require explicit human selection.


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
```


For machine-oriented output:


```bash
python tools/stack.py adoption-plan --json
```


The adoption plan reports active/deferred component state, authoritative repository, pinned template revision, and the exact upstream manifest that owns upgrade classification.


## Upgrade safety


Starter does **not** copy AHICP or PPF ownership lists. For each active component, an agent must fresh-read the component manifest at its pinned `template_source_commit`. That upstream manifest is authoritative for `upstream-managed`, `merge-managed`, and `project-owned` paths.
