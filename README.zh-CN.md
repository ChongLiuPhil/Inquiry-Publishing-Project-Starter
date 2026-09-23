# Inquiry Publishing Project Starter

**第一次了解整个体系：** 从 [AHICP 主页](https://inquirystack.philohub.workers.dev/) 开始；那里提供完整使用指南和可直接交给 AI 的启动指令。

Starter 主要面向 AI 和配置工作；第一次了解体系时，不需要先读这些技术细节。

**机器入口：** [公共 Agent 页面](https://inquirystack.philohub.workers.dev/agent/) · [机器描述文件](https://inquirystack.philohub.workers.dev/agent/entry.json)

这是 AHICP、PPF 与 Vault Interface 的**组合、采用和升级层**，不是第四套规范。

**公共项目主页：** [AHICP](https://inquirystack.philohub.workers.dev/) · [PPF](https://inquirystack.philohub.workers.dev/ppf/) · [Vault Interface](https://inquirystack.philohub.workers.dev/vault-interface/) · [Starter](https://inquirystack.philohub.workers.dev/starter/)

**体系与 AI 配置入口：** [`docs/ECOSYSTEM.zh-CN.md`](docs/ECOSYSTEM.zh-CN.md) · [`ecosystem.yaml`](ecosystem.yaml) · [`Agent 调取契约`](docs/AGENT_RETRIEVAL_CONTRACT.zh-CN.md) · [`llms.txt`](docs/llms.txt) · [`Cloudflare 操作指南`](docs/CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md)

**新项目默认配置：** 完整 AHICP + 完整 PPF + Vault Interface。原创或未发布源文件默认 private（私有）；Continuous Web 可以同时准备，但在明确公开发布前默认 restricted + authenticated（受限并需要认证）。精简配置（profile）必须由使用者明确选择。

## 权威边界

- AHICP：探究、证据、决定、项目记忆和 AI 协作规则；
- PPF：源内容 → 构建 → 发布 → 正式版本 → 归档；
- Vault Interface：公开、平台无关的 `project.yaml` / `website.yaml` 元数据接口；
- Starter：只描述如何组合、采用和升级这些独立上游。

## Stack v2

Stack v2 把三件容易混淆的事分开记录：

- `template_source_commit`：组合与升级所依据的上游模板 / manifest 版本；
- `project_adopted_commit`：项目真正采用的语义框架版本（适用时）；
- `adoption_state`：`active`、`deferred` 或 `not-applicable`。

因此，旧项目可以复用已有结构，某个组件也可以暂缓采用；同时还能明确区分“这次升级参考哪一版模板”和“项目实际上接受了哪一版规则”。

## Profiles

- `full-research-publication`：三者全部 active，**新项目默认**
- `research-only`：Vault Interface + AHICP，必须显式选择精简 profile
- `publishing-only`：Vault Interface + PPF，必须显式选择精简 profile
- `research-book`：Vault Interface + AHICP；PPF 为可选组件，必须显式选择精简 profile

Profile 只描述组件组合，不代表项目价值高低。

## 机器检查

```bash
python -m pip install -r requirements-validation.txt
make stack-check
make stack-test
make upstream-check
make adoption-plan
```

机器计划会报告每个组件是否 active / deferred、权威仓库、固定模板版本，以及升级前需要重新读取的上游 ownership manifest。

## Ownership 规则

Starter **不再复制** AHICP/PPF 的 ownership 列表。升级前必须读取每个 active component 在 `template_source_commit` 所固定的上游 manifest，并以其中的 `upstream-managed`、`merge-managed`、`project-owned` 分类为准。

可靠的既有文件应优先映射到相应功能角色；不要只因为模板长得不同，就再复制一套相同内容作为第二个权威来源。人类已批准决定、publication authorization、canonical identity 与 provider actual state 必须保留，除非人类明确改变。

## Provenance

GitHub Template 生成的新仓库有自己的新历史，所以**下游项目 HEAD 不是 Starter source revision**。

采用时必须把：

`starter.adopted_commit: TEMPLATE_SOURCE_COMMIT_AT_ADOPTION`

替换成实际采用的 Starter commit。只要占位符还在，`freeze_stack_lock.py` 就会失败，而不会把下游 HEAD 错写成 Starter revision。

## GitHub Template Repository

本仓库已经作为 GitHub Template Repository 使用。新项目可以从 **Use this template** 开始，再记录真实 Starter source revision 并按 adoption plan 完成组合。


`make upstream-check` 会通过 GitHub fresh-read 固定 revision 的上游 manifest，直接确认 AHICP/PPF/Vault Interface 的 profile/version 在该 revision 中真实存在。Starter 不复制一份 profile 清单作为第二真值源。

## 许可

本仓库采用**非商业双重许可模式**，目的是支持个人学习、教育、研究、公益以及其他非商业复用，同时保留商业授权权利。

- 软件、脚本、Schema、自动化、机器可读配置和可执行模板：**PolyForm Noncommercial License 1.0.0**；
- 说明文档、规范、图示、教育材料与方法论内容：**CC BY-NC-SA 4.0**；
- 商业使用需要另行取得商业许可。

仓库级权威许可边界见 [LICENSE.md](LICENSE.md) 与 [COMMERCIAL-LICENSING.md](COMMERCIAL-LICENSING.md)。
