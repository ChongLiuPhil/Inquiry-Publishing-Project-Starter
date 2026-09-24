# Inquiry Publishing Stack：体系与 AI 配置入口

本仓库是四个逻辑独立组件的组合入口：

| 组件 | 责任 | 公共入口 |
| --- | --- | --- |
| AHICP | 探究、证据、决定、项目记忆与 AI 协作 | [主页](https://inquirystack.philohub.workers.dev/) · [仓库](https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol) |
| PPF | 以源文件为中心的出版、发布、归档和 Continuous Web | [主页](https://inquirystack.philohub.workers.dev/ppf/) · [仓库](https://github.com/ChongLiuPhil/Personal-Publishing-Framework) |
| Vault Interface | 与提供商无关的公共元数据 Schema 与验证器 | [主页](https://inquirystack.philohub.workers.dev/vault-interface/) · [仓库](https://github.com/ChongLiuPhil/Vault-interface) |
| Starter | 组合、采用、项目 Provisioning 编排、配置方案与升级 | [主页](https://inquirystack.philohub.workers.dev/starter/) · [仓库](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter) |

四者保持逻辑独立。互相链接建立的是可发现性与共同采用路径，不会把某个组件的规范权威转移给另一个组件。

## 了解体系与配置项目是两件不同的事

整个体系有意区分两个入口角色：

- **先从 AHICP 了解体系：** [AHICP 公共主页](https://inquirystack.philohub.workers.dev/) 提供完整使用指南，解释这套体系解决什么问题以及怎样开始。
- **让 AI 从 Starter 开始配置：** 使用本仓库的 `ecosystem.yaml`、profiles、stack files、Agent Retrieval Contract 与 Project Provisioning Contract 执行项目组合、采用、低人工 Provisioning、升级、部署和状态恢复。

AHICP 负责解释方法和使用方式；Starter 保留精确的机器配置契约，两者互相链接但不互相替代。

## 默认配置基线

新项目默认配置是：

~~~text
AHICP（完整）
+ PPF（完整）
+ Vault Interface（公共元数据适配器）
+ 项目自身内容
~~~

项目通过 project-stack.yaml 记录真实采用状态，不复制出与上游规范竞争的第二真值源。

`full-research-publication` 是新项目默认 profile。精简 profile 仍然保留，但 AI Agent 只有在使用者明确选择时才能使用；不能因为项目看起来简单就自动省略 AHICP 或 PPF。

普通新项目首选 infrastructure profile 是 `workers-builds-native`：在个人 `ChongLiuPhil` GitHub 账号下保持 private repository，每项目完成一次短人工 Cloudflare Git connection，默认使用 Worker-scoped Access，并在 Preview 独立保护验收前保持 disabled。第一次 restricted deployment 后，还必须验证第二次 push 无需重新授权即可自动部署，才能把连接标记为 operationally verified。Public release、repository 公开、reader expansion、domain/DNS authority、Provider scope 扩大与 paid-plan change 仍由人保留。

`agent-provisioned-external-ci` 继续作为高级可选 Profile；只有项目明确需要 one-Worker deployment credential 隔离并愿意维护额外 Platform Authorization / Trusted Secret Broker 时才采用。

Vault Interface 是适配层，不替代 AHICP 或 PPF。

## 隐私与发布边界

- 未发布手稿、原创研究、个人工作记忆、凭据和其他具有版权属性的源资产默认 private。
- 公共框架仓库只包含可复用方法、Schema、模板、验证器和已批准公开文档，不包含私人项目状态。
- private 源仓库仍可拥有 Continuous Web。
- 未发布或过渡阶段 Web 默认 restricted。
- 读者认证属于访问层。仓库只保存 policy reference，不保存密码、API token、私钥、OTP、恢复码或其他秘密。
- 统一阅读凭据可作为过渡性策略，但秘密值必须留在提供商侧。
- 从 restricted 转为 public 需要人类明确授权，而且不意味着源仓库必须改成 public。
- 私人控制平面只能通过获得授权的项目配置被引用，不复制进公共 Starter。

## 公共页面与 AI 调取

四个公共组件都应能互相发现，并指向同一个权威 ecosystem 契约。

机器调取入口：

- [ecosystem.yaml](../ecosystem.yaml)
- [AGENT_RETRIEVAL_CONTRACT.zh-CN.md](AGENT_RETRIEVAL_CONTRACT.zh-CN.md)
- [PROJECT_PROVISIONING_CONTRACT.zh-CN.md](PROJECT_PROVISIONING_CONTRACT.zh-CN.md)
- [llms.txt](llms.txt)

公共页面只能提高可发现性，不能强制任意 AI 系统自动抓取其他资源。因此，本契约定义的是遵循仓库指令的 Agent 应执行的调取行为。

## Agent 调取契约

AI agent 从任意组件主页或仓库进入时，必须：

1. 确认当前组件并读取该仓库 ecosystem.yaml；
2. 读取 canonical Starter ecosystem 与 AGENT_RETRIEVAL_CONTRACT；
3. 恢复四个组件的责任和公共入口；
4. 面对下游项目时读取所选 Starter profile、`project-stack.yaml`、lock，以及存在时的 `project-provisioning.yaml`；
5. 面对新项目时读取 Project Provisioning Contract 与固定版本 PPF 的每项目 setup contract；只有显式选择高级 Profile 时才读取私人 platform-authorization state；
6. fresh-read 每个 active 上游组件的固定 revision manifest；
7. 其他私人项目状态仍只在相应访问已获授权后读取；
8. 始终区分 proposal、authorization、execution、verification 与 durable write-back。

沿公共链接调取是一套阅读协议，不构成私人仓库或部署系统访问权限。

## 公共网页的交付平台

四个公共框架栏目现由**一个 Cloudflare Worker** 在 `https://inquirystack.philohub.workers.dev/` 交付；GitHub 继续作为权威源文件、版本历史和 CI 平台。原框架 GitHub Pages 站点已停用；上一已验证 Worker 版本是回滚点。

已批准的切换、线上验收与回滚遵循 [CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.zh-CN.md](CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.zh-CN.md) 和机器可读的 [cloudflare-public-delivery.yaml](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/blob/main/templates/cloudflare-public-delivery.yaml)。所选 `workers.dev` 地址免费；自定义域名仍可选。

以后再改变域名或可见性，仍须单独决定、验证并保留回滚路径。

## Continuous Web 与 Cloudflare

新项目编排契约见 [PROJECT_PROVISIONING_CONTRACT.zh-CN.md](PROJECT_PROVISIONING_CONTRACT.zh-CN.md)。详细 Cloudflare 操作契约见 [CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md](CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md)。默认执行路径是文档化的每项目 Workers Builds bootstrap；Browser Agent 与高级自动化 handoff 只作为可选实现辅助。

Starter 只记录 Provisioning 意图与授权边界；真正可执行的 GitHub/Cloudflare Provider 逻辑由 PPF 保持权威。Provider credential 明文绝不能进入语言模型；默认 Workers Builds 路线让 deployment credential 保持 Provider-managed。

AI agent 在要求人类执行 Cloudflare 操作前，必须给出编号的操作者级步骤，指出准确目标账户/项目/域名和受影响层，解释凭据范围与数据传输，明确哪些秘密不得发送给 AI，定义完成证据，并给出回滚路径。

Provider-specific 细节应从当前 PPF Cloudflare runbook 中读取；必要时还要核对 Cloudflare 当前 UI 或官方文档，而不能猜测。
