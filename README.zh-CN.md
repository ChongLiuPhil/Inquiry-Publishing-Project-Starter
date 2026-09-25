# Inquiry Publishing Project Starter

**第一次了解整个体系：** 从 [AHICP 主页](https://inquirystack.philohub.workers.dev/) 开始；那里提供完整使用指南和可直接交给 AI 的启动指令。

Starter 主要面向 AI 和配置工作；第一次了解体系时，不需要先读这些技术细节。

**机器入口：** [公共 Agent 页面](https://inquirystack.philohub.workers.dev/agent/) · [机器描述文件](https://inquirystack.philohub.workers.dev/agent/entry.json)

这是 AHICP、PPF 与 Vault Interface 的**组合、采用、升级和项目 Provisioning 编排层**，不是第四套规范。

**公共项目主页：** [AHICP](https://inquirystack.philohub.workers.dev/) · [PPF](https://inquirystack.philohub.workers.dev/ppf/) · [Vault Interface](https://inquirystack.philohub.workers.dev/vault-interface/) · [Starter](https://inquirystack.philohub.workers.dev/starter/)

**体系与 AI 配置入口：** [`docs/ECOSYSTEM.zh-CN.md`](docs/ECOSYSTEM.zh-CN.md) · [`ecosystem.yaml`](ecosystem.yaml) · [`Agent 调取契约`](docs/AGENT_RETRIEVAL_CONTRACT.zh-CN.md) · [`项目自动配置契约`](docs/PROJECT_PROVISIONING_CONTRACT.zh-CN.md) · [`llms.txt`](docs/llms.txt) · [`Cloudflare 操作指南`](docs/CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md)

**新项目默认配置：** 完整 AHICP + 完整 PPF + Vault Interface。Downstream repository 默认创建在个人 `ChongLiuPhil` GitHub 账号下，使用 `owner_type: user` 与 `visibility: private`；原创或未发布源文件继续保持 private。默认 infrastructure profile 为 `workers-builds-native` + `private-project-quota-saver`：允许每个项目一次短而明确的人类 GitHub → Cloudflare bootstrap，给 Worker 配置 Access；自动 main Web build 交给 Cloudflare Workers Builds；content-only 改动不启动 GitHub Actions；只有目标分支为 `main` 的配置 PR 自动跑一个轻量 gate；heavy GitHub workflow 手动执行；自动成功 run 不上传 artifact，手动 publication artifact 默认保留 1 天。然后验证第二次 push 无需重新授权即可自动部署。`agent-provisioned-external-ci` 继续作为高级可选 Profile。Public release 与任何付费 Actions / billing 变化仍是独立的人类决定。精简 Stack Profile 必须由使用者明确选择。

## 权威边界

- AHICP：探究、证据、决定、项目记忆和 AI 协作规则；
- PPF：源内容 → 构建 → 发布 → 正式版本 → 归档；
- Vault Interface：公开、平台无关的 `project.yaml` / `website.yaml` 元数据接口；
- Starter：描述如何组合、采用、Provisioning 编排和升级这些独立上游；真正的 Provider execution 仍由固定版本 PPF 实现。

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
make provisioning-contract-check
```

机器计划会报告每个组件是否 active / deferred、权威仓库、固定模板版本、升级前需要重新读取的上游 ownership manifest，以及存在时的 Provisioning Profile。

## 项目自动配置

新的 downstream 项目还记录 `project-provisioning.yaml`。公共 Schema / Template 只描述非秘密意图。默认 `workers-builds-native` 路线同时记录 `ci_cost_profile: private-project-quota-saver`，不要求 platform standing authorization；只有显式选择依赖它的高级 Profile 时，才读取 private platform-authorization state。

```bash
python tools/project_provisioning.py validate
python tools/project_provisioning.py plan --request project-provisioning.yaml --json
```

默认 `workers-builds-native` Profile 即使没有账户级 Platform Authorization，也会生成 `READY_FOR_PROJECT_BOOTSTRAP`，并把 `ciCostProfile: private-project-quota-saver` 交给 PPF。随后按照固定版本 PPF 的每项目配置指南，把 private repository 连接到 Workers Builds、给 Worker 配置 Access、验证第一次 restricted deployment，再验证第二次 push 无需重新授权即可部署。Content-only 改动不应消耗 GitHub Actions 分钟；配置 PR 使用薄 contract gate；重型 Actions validation 手动执行。Trusted Secret Broker 只属于高级可选 External-CI Profile。

详见 [`docs/PROJECT_PROVISIONING_CONTRACT.zh-CN.md`](docs/PROJECT_PROVISIONING_CONTRACT.zh-CN.md) 与 [`docs/PROJECT_PROVISIONING_ACCEPTANCE.zh-CN.md`](docs/PROJECT_PROVISIONING_ACCEPTANCE.zh-CN.md)。

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
