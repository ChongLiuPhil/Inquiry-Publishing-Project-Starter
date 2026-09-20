# Inquiry Publishing Stack：体系与 Agent 入口

本仓库是四个逻辑独立组件的组合入口：

| 组件 | 责任 | 公共入口 |
| --- | --- | --- |
| AHICP | 人类主导、AI 辅助的探究与创作治理 | [主页](https://chongliuphil.github.io/AI-Assisted-Human-Inquiry-and-Creation-Protocol/) · [仓库](https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol) |
| PPF | 以源文件为中心的出版、发布、归档和 Continuous Web | [主页](https://chongliuphil.github.io/Personal-Publishing-Framework/) · [仓库](https://github.com/ChongLiuPhil/Personal-Publishing-Framework) |
| Vault Interface | 与提供商无关的公共元数据 Schema 与验证器 | [主页](https://chongliuphil.github.io/Vault-interface/) · [仓库](https://github.com/ChongLiuPhil/Vault-interface) |
| Starter | 组合、采用、profile 与升级 | [主页](https://chongliuphil.github.io/Inquiry-Publishing-Project-Starter/) · [仓库](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter) |

四者保持逻辑独立。互相链接建立的是可发现性与共同采用路径，不会把某个组件的规范权威转移给另一个组件。

## 默认配置基线

新配置项目的默认状态是：

~~~text
AHICP（完整）
+ PPF（完整）
+ Vault Interface（公共元数据适配器）
+ 项目自身内容
~~~

项目通过 project-stack.yaml 记录真实采用状态，不复制出与上游规范竞争的第二真值源。

full-research-publication 是新项目默认 profile。精简 profile 仍然保留，但 AI agent 只有在人类明确选择时才能使用；不能因为项目看起来简单而静默省略 AHICP 或 PPF。

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

## 人类与 AI 可发现性

四个公共组件都应展示相同的四个公共主页，并指向同一个 canonical ecosystem contract。

机器调取入口：

- [ecosystem.yaml](../ecosystem.yaml)
- [AGENT_RETRIEVAL_CONTRACT.zh-CN.md](AGENT_RETRIEVAL_CONTRACT.zh-CN.md)
- [llms.txt](llms.txt)

公共页面只能提高可发现性，不能强制任意 AI 系统自动抓取其他资源。因此，本契约定义的是遵循仓库指令的 Agent 应执行的调取行为。

## Agent 调取契约

AI agent 从任意组件主页或仓库进入时，必须：

1. 确认当前组件并读取该仓库 ecosystem.yaml；
2. 读取 canonical Starter ecosystem 与 AGENT_RETRIEVAL_CONTRACT；
3. 恢复四个组件的责任和公共入口；
4. 面对下游项目时读取所选 Starter profile、project-stack.yaml 与 lock；
5. fresh-read 每个 active 上游组件的固定 revision manifest；
6. 只有在人类明确授权后才检查私人项目状态；
7. 始终区分 proposal、authorization、execution、verification 与 durable write-back。

沿公共链接调取是一套阅读协议，不构成私人仓库或部署系统访问权限。

## Continuous Web 与 Cloudflare

详细操作契约见 [CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md](CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md)。

AI agent 在要求人类执行 Cloudflare 操作前，必须给出编号的操作者级步骤，指出准确目标账户/项目/域名和受影响层，解释凭据范围与数据传输，明确哪些秘密不得发送给 AI，定义完成证据，并给出回滚路径。

Provider-specific 细节应从当前 PPF Cloudflare runbook 中读取；必要时还要核对 Cloudflare 当前 UI 或官方文档，而不能猜测。
