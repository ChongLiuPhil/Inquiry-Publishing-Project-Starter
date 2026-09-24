# Agent 协作契约

在配置、采用、升级、发布或操作项目之前，先阅读：

1. docs/ECOSYSTEM.zh-CN.md
2. ecosystem.yaml
3. docs/AGENT_RETRIEVAL_CONTRACT.zh-CN.md
4. docs/AI_ADOPTION_WORKFLOW.zh-CN.md
5. 每个新项目或涉及项目基础设施 Provisioning 时读取 docs/PROJECT_PROVISIONING_CONTRACT.zh-CN.md
6. 涉及 Continuous Web 或 Cloudflare 时读取 docs/CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md
7. 需要人类/账户所有者动作时读取 docs/CLOUDFLARE_MINIMAL_HUMAN_HANDOFF.zh-CN.md
8. 由 Browser Agent / Work 执行 provider UI 时读取 docs/CLOUDFLARE_WORK_AGENT_HANDOFF.zh-CN.md

新项目默认基线是 **完整 AHICP + 完整 PPF + Vault Interface + 项目自身内容**。默认使用 full-research-publication；只有在人类明确选择时才使用精简 profile。平台 bootstrap 完成后，基础设施 Provisioning 首选 `agent-provisioned-external-ci`。不得因为项目看起来简单而静默省略组件，也不得在 verified standing authorization 已覆盖另一个 private/restricted 项目创建时反复要求账户级授权。

原创未发布内容、凭据、私人工作记忆和私人控制平面状态必须留在公共仓库之外。原创项目的源仓库默认 private。Continuous Web 仍可启用，但未发布或过渡阶段 Web 默认 restricted，并使用 access-policy reference，而不是把秘密写入 Git。

从任意公共组件入口进入时，在跨组件配置前先恢复四组件生态。公共链接只授权读取公共信息，不授权私人状态访问。

执行任何 Cloudflare 操作前，必须说明准确目标、受影响层、数据流、凭据范围、人类批准边界、验证检查与回滚。首选 Profile 的 project deployment credential 必须经 trusted Secret Broker 传递；模型绝不能接收 token 明文。需要人类操作 UI 时，必须提供编号的操作者级步骤，而不是笼统要求。绝不要求人类把密码、token、私钥、恢复码或其他秘密发送到聊天。

始终区分 proposal、authorization、execution、verification 与 durable write-back。
