# Agent 调取契约

## 0. 权威机器入口

稳定的公共机器入口页面是：

https://chongliuphil.github.io/Inquiry-Publishing-Project-Starter/agent/

使用者可以只把这个 URL 交给 AI Agent。Agent 随后必须自行读取权威 ecosystem 与本调取契约，恢复四个组件的关系，并按下文规则继续。公共页面负责提供稳定入口；GitHub 中受版本控制的 ecosystem 与契约仍是权威来源。

本文是 Inquiry Publishing Stack 的跨仓库规范调取契约。

它不会把 AHICP、PPF、Vault Interface 与 Starter 合并成一套规范，而是规定 AI agent 在配置、升级、发布或操作项目之前，如何恢复四者之间的关系。

## 1. 从任何公共入口进入

Agent 可能从以下任意入口进入：

- AHICP、PPF、Vault Interface 或 Starter 的公共主页；
- 四个 GitHub 仓库中的任意一个；
- README、AGENTS.md、ecosystem.yaml 或 llms.txt；
- 声明采用一个或多个组件的下游项目。

只要任务涉及跨组件配置，Agent 都必须先恢复完整公共生态，而不能只依据当前仓库作判断。

## 2. 必要调取顺序

1. 确认当前组件。
2. 阅读当前仓库的 ecosystem.yaml 与体系说明。
3. 阅读 Starter 的本调取契约和权威 `ecosystem.yaml`。
4. 恢复四个公共组件及其责任：
   - AHICP：探究、证据、决定、项目记忆与 AI 协作；
   - PPF：以源文件为中心的出版生命周期与 Continuous Web；
   - Vault Interface：与平台无关的公共元数据接口；
   - Starter：组合、采用、配置方案与升级层。
5. 如果面对下游项目，读取 `project-stack.yaml`、所选 profile 与 lock 文件。
6. 对每个 active 的 AHICP 或 PPF 组件，在配置或升级前重新读取固定 revision 对应的上游 manifest 或 template manifest。
7. 只有在人类明确授权后才读取私人项目状态。
8. 在写入外部状态前，明确区分提议（proposal）、授权（authorization）、执行（execution）、验证（verification）和持久写回（durable write-back）。
9. 涉及 Cloudflare 时，先读取共享的 Continuous Web / Cloudflare 指南，以及所选部署 profile 对应的 PPF 服务商操作说明。

沿公共链接阅读只是一项调取指令，不构成私人仓库、私人 Vault、提供商账户、凭据、未发布源文件或部署控制平面的访问授权。

## 3. 新项目默认基线

除非使用者明确选择精简 profile，新配置项目默认采用：

~~~text
完整 AHICP
+ 完整 PPF
+ Vault Interface 公共元数据适配器
+ 项目自身内容
~~~

精简 profile 仍然可用，但必须由使用者明确选择。Agent 不得因为项目“看起来简单”就自动省略 AHICP 或 PPF。

## 4. 默认隐私与发布姿态

对于原创、未发布、研究、手稿或其他具有版权属性的项目内容：

- 权威源仓库默认 private；
- 仍然可以准备并部署 Continuous Web；
- 未发布或过渡阶段 Web 默认 restricted；
- 读者认证在访问层实现，不通过 Git 提交密码；
- 仓库只记录 policy reference，不记录秘密凭据；
- 从 restricted 转为 public 必须得到使用者明确授权；
- Web 公开不意味着源仓库也必须公开。

当前可以暂时使用统一阅读凭据，但其秘密值必须留在提供商侧，不得进入 Git、日志、Issue、Pull Request 或聊天。

## 5. Agent 在实际配置前应能说明的状态

在实质配置或升级前，Agent 应能说明：

- 从哪个组件入口进入；
- 四个组件的责任与公共入口；
- 下游所选 profile；
- active、deferred 与 not-applicable 组件；
- 固定的上游 revision；
- 源仓库隐私与 Web 可见性；
- 当前发布授权状态；
- Cloudflare 部署 profile 与访问策略；
- 哪些操作已经授权、哪些仍由人保留；
- 哪些服务商实际状态仍需验证。

如果无法恢复这些事实，应把它视为配置缺陷，而不是自行猜测。

## 6. Cloudflare 需要人工操作时的交接标准

当某项 Cloudflare 操作无法通过已经授权的工具直接完成时，Agent 不得只说“配置 Cloudflare”或“启用 Access”，而应提供完整的编号操作步骤，包括：

1. 登录位置以及准确的账户、项目/Worker、域名目标；
2. 当前 Dashboard 应进入的区域或 UI 路径；
3. 要选择或填写的非秘密值，以及哪些值来自项目契约；
4. 哪些秘密绝不能发送给 AI；
5. 使用者完成后应看到的成功状态；
6. Agent 随后会验证什么；
7. 如果涉及路由、发布或访问控制，如何回滚。

如果 Cloudflare 当前 UI 与已有 runbook 不同，Agent 必须检查当前 UI 或官方文档，不能凭记忆猜路径。

## 7. 四个权威公共入口

- AHICP: https://chongliuphil.github.io/AI-Assisted-Human-Inquiry-and-Creation-Protocol/
- PPF: https://chongliuphil.github.io/Personal-Publishing-Framework/
- Vault Interface: https://chongliuphil.github.io/Vault-interface/
- Starter: https://chongliuphil.github.io/Inquiry-Publishing-Project-Starter/

机器可读生态：
https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/blob/main/ecosystem.yaml

Continuous Web / Cloudflare 指南：
https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/blob/main/docs/CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md
