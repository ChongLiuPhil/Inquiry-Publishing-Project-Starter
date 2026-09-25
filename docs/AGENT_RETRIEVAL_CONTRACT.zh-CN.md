# Agent 调取契约

## 0. 权威机器入口

稳定的公共机器入口页面是：

https://inquirystack.philohub.workers.dev/agent/

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
5. 如果面对下游项目，读取 `project-stack.yaml`、所选 profile、lock 文件，以及存在时的 `project-provisioning.yaml`。
6. 面对**新项目**时，读取权威 Project Provisioning Contract；如果 Request 依赖 platform standing authorization，只有在该 control-plane access 已获授权后才读取私人 platform-authorization state。
7. 对每个 active 的 AHICP 或 PPF 组件，在配置或升级前 fresh-read 固定 revision 对应的上游 manifest / template manifest。
8. 其他私人项目状态仍只在人类明确授权后读取。
9. 在写入外部状态前，明确区分 proposal、authorization、execution、verification 与 durable write-back。
10. 涉及 Cloudflare 时，读取共享 Continuous Web / Cloudflare 指南，以及所选 deployment profile 对应的 PPF Provider contract。

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

普通新建完整 Stack 项目首选 infrastructure profile 为 `workers-builds-native` + `private-project-quota-saver`：使用个人 `ChongLiuPhil` GitHub 账号、repository 保持 private，以 `human-assisted-once-per-project` 完成 GitHub → Cloudflare 连接，默认采用 `worker-scoped-access`，Preview 在独立验收前保持 disabled，并要求第二次 content-only push 能在无需重新授权的情况下自动部署。在 quota-saver Profile 中，content-only 改动不启动 GitHub Actions，只有目标分支为 `main` 的配置 Pull Request 自动运行一个轻量 contract job，`main` 不触发重复的 GitHub Web build，heavy GitHub workflow 手动运行，自动成功 run 不上传 artifact，手动 publication artifact 保留 1 天，Cloudflare Workers Builds 负责唯一自动 production Web build。`agent-provisioned-external-ci` 继续作为使用 `external-ci-required` 的高级可选 Profile；只有这个高级 Profile 才要求 reusable platform standing authorization、作为 Provisioning 前置条件的 account-wide Access，以及 trusted Secret Broker。Public framework repository 使用 `full-validation` 作为 full-CI 成本 Profile。

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
- Cloudflare deployment profile 与 access policy；
- 适用时的 project provisioning profile、CI cost profile、bootstrap mode 与 `project-provisioning.yaml` 状态；
- 对默认 Native Profile：repository owner / visibility、Workers Builds repository connection、实际 Access mode、`private-project-quota-saver` 行为、第一次 restricted deployment 验证、第二次 push 无需重新授权验证；
- 只有高级可选 External-CI Profile 才报告：platform standing authorization 是否覆盖当前 GitHub owner / Cloudflare scope，以及 trusted Secret Broker 与隔离 token-minting boundary 是否 verified；
- 哪些操作已经授权、哪些仍由人保留；
- 哪些 Provider actual state 仍需验证。

如果无法恢复这些事实，应把它视为配置缺陷，而不是自行猜测。

Private downstream 项目不能把 GitHub Actions 当作迭代调试环境。Agent 应批量完成相关编辑、运行可用 preflight、检查完整 diff，再只触发预定的薄 CI。Run 失败时先读完整 failure set、批量修复并尽量只 rerun failed work。不得为 content-only 改动制造 Actions run，也不得在没有人类明确授权时开启付费 Actions usage。

## 6. 公共网页迁移规则

对于四个公共框架网站，Cloudflare Workers 是首选交付平台，GitHub 继续作为权威源文件、版本历史和 CI 平台。

已批准架构把四个仓库组合为**一个网站、一个活动 Worker**。用户另行批准 `https://inquirystack.philohub.workers.dev/` 作为正式人类入口，`/agent/` 作为机器入口；四个规范权威仍保持独立。必须读取 `docs/UNIFIED_PUBLIC_SITE.zh-CN.md` 与 v3 迁移计划。`site/sources.lock.json` 只固定网站来源，不替代下游采用锁。

所选 `workers.dev` 地址免费且不需 DNS 修改。原框架 GitHub Pages 站点已停用；获批 Worker 是唯一公共网站入口。回滚使用上一已验证 Worker 版本或经过审核的 revert。必须读取 `templates/cloudflare-public-delivery.yaml` 的实际迁移与验收状态；批准和 CI 成功不能单独证明线上切换完成。受限预览继续关闭，等待独立 Access 验收。

## 7. Cloudflare 需要人工操作时的交接标准

当某项 Cloudflare 操作无法通过已经授权的工具直接完成时，Agent 不得只说“配置 Cloudflare”或“启用 Access”，而应提供完整的编号操作步骤，包括：

1. 登录位置以及准确的账户、项目/Worker、域名目标；
2. 当前 Dashboard 应进入的区域或 UI 路径；
3. 要选择或填写的非秘密值，以及哪些值来自项目契约；
4. 哪些秘密绝不能发送给 AI；
5. 使用者完成后应看到的成功状态；
6. Agent 随后会验证什么；
7. 如果涉及路由、发布或访问控制，如何回滚。

如果 Cloudflare 当前 UI 与已有 runbook 不同，Agent 必须检查当前 UI 或官方文档，不能凭记忆猜路径。

## 8. 四个权威公共入口

- AHICP: https://inquirystack.philohub.workers.dev/
- PPF: https://inquirystack.philohub.workers.dev/ppf/
- Vault Interface: https://inquirystack.philohub.workers.dev/vault-interface/
- Starter: https://inquirystack.philohub.workers.dev/starter/

机器可读生态：
https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/blob/main/ecosystem.yaml

Continuous Web / Cloudflare 指南：
https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/blob/main/docs/CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md
