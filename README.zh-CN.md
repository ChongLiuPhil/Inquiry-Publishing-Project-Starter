# Inquiry Publishing Project Starter

这是 AHICP、PPF 与 Vault Interface 的**组合、采用和升级层**，不是第四套规范。

## 权威边界

- AHICP：人类主导、AI 辅助的探究与创作治理；
- PPF：source → build → publish → release → archive；
- Vault Interface：公开、中性的 `project.yaml` / `website.yaml` 接口；
- Starter：只描述如何组合、采用和升级这些独立上游。

## Stack v2

v2 明确区分三件不能混在一起的事：

- `template_source_commit`：组合与升级机械操作所依据的上游模板/manifest revision；
- `project_adopted_commit`：项目真正采用的语义框架 revision（适用时）；
- `adoption_state`：`active`、`deferred` 或 `not-applicable`。

因此，旧项目的 functional mapping、PPF 暂缓采用、以及“模板来源版本”和“项目曾批准版本”不同，都可以由同一正式 Schema 表达。

## Profiles

- `research-only`：Vault Interface + AHICP
- `publishing-only`：Vault Interface + PPF
- `research-book`：Vault Interface + AHICP；PPF 为可选组件
- `full-research-publication`：三者全部 active

Profile 是组件组合，不是价值等级。

## 机器检查

```bash
python -m pip install -r requirements-validation.txt
make stack-check
make stack-test
make upstream-check
make adoption-plan
```

机器计划会报告每个组件的 active/deferred 状态、权威仓库、固定模板 revision，以及需要 fresh-read 的上游 ownership manifest。

## Ownership 规则

Starter **不再复制** AHICP/PPF 的 ownership 列表。升级前必须读取每个 active component 在 `template_source_commit` 所固定的上游 manifest，并以其中的 `upstream-managed`、`merge-managed`、`project-owned` 分类为准。

可靠的既有文件优先 functional mapping；不得因为模板形式一致而制造第二套真值源。人类已批准决定、publication authorization、canonical identity 与 provider actual state 必须保留，除非人类明确改变。

## Provenance

GitHub Template 生成的新仓库有自己的新历史，所以**下游项目 HEAD 不是 Starter source revision**。

采用时必须把：

`starter.adopted_commit: TEMPLATE_SOURCE_COMMIT_AT_ADOPTION`

替换成实际采用的 Starter commit。只要占位符还在，`freeze_stack_lock.py` 就会失败，而不会把下游 HEAD 错写成 Starter revision。

## GitHub Template Repository

本仓库已经作为 GitHub Template Repository 使用。新项目可以从 **Use this template** 开始，再记录真实 Starter source revision 并按 adoption plan 完成组合。


`make upstream-check` 会通过 GitHub fresh-read 固定 revision 的上游 manifest，直接确认 AHICP/PPF/Vault Interface 的 profile/version 在该 revision 中真实存在。Starter 不复制一份 profile 清单作为第二真值源。
