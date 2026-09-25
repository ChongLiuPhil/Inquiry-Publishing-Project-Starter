# 项目记忆与 Bootstrap 写回契约

**状态：** 新项目跨组件持久化的权威规则  
**原则：** 仓库状态高于聊天、账号记忆与 Agent 的会话记忆。

本契约的目的，是让一个完全看不到上一轮对话的新 Agent，仅凭项目仓库就能恢复当前 GitHub → Cloudflare 配置状态。

任何具有运行意义的内容都不得只存在于 AI 对话中。

## 1. 四层持久状态

完整栈项目使用四类互补的持久记录：

1. **`project-provisioning.yaml` — 预期配置**
   - 选择的 infrastructure profile；
   - 预期 GitHub owner / repository / privacy；
   - 预期 Cloudflare Worker / Access mode；
   - publication authorization boundary。

2. **`project-bootstrap-state.yaml` — 实际运行 Bootstrap 状态**
   - 哪些人工 / Provider 步骤 pending、completed 或 blocked；
   - repository / Workers Builds / Access 当前状态；
   - 第一次 deployment 与第二次 push 验收状态；
   - 非秘密 evidence 与 rollback reference。

3. **AHICP Working Memory — 当前工作与续接点**
   - `docs/working-memory/current-focus.zh-CN.md`；
   - `docs/working-memory/task-plan.zh-CN.md`；
   - `docs/working-memory/work-log.zh-CN.md`。

4. **AHICP Long-Term Memory / Decision Log — 持久的人类决定**
   - publication 决定；
   - scope / permission 变化；
   - reader / audience policy 决定；
   - 其他会改变项目政策、而不只是报告 Provider 状态的决定。

不得把这些角色压缩成一段聊天摘要。

## 2. 交给人操作以前必须先写回

Agent 在要求人类去 GitHub / Cloudflare UI 操作以前，**必须先把待做步骤写入项目持久状态**。

至少要：

- 将对应 `project-bootstrap-state.yaml -> human_steps.<step>.status` 设为 `waiting-human`；
- 将项目 `status` 设为 `waiting-human`；
- 写入准确 `guide_ref`；
- 在 AHICP Task Plan 中记录待人操作与准确的 Agent 恢复条件；
- 如果它已经成为当前主要 blocker，同时更新 Current Focus。

人类不应需要翻聊天记录才能知道下一步点哪里。

## 3. 人完成操作以后也必须写回

人类回复“已完成”后，Agent 在工具允许时必须先验证实际 Provider / repository state。

只有验证后才可以：

- 把 human step 标记为 `completed`（或 `not-required`）；
- 更新对应 GitHub / Cloudflare actual-state 字段；
- 写入非秘密 completion evidence；
- 更新 `last_updated`；
- 更新 AHICP Task Plan 与 Current Focus；
- Bootstrap 有实质推进时，在 Work Log 追加高层里程碑。

“人说完成了”是开始验证的信号，本身不等于 Provider state 已经验证。

## 4. 人工 UI 操作说明必须持久存在

任何需要人类完成的 Provider 操作，都必须有仓库中的操作者指南，至少包含：

- 准确 target account / repository / Worker；
- 当前 Dashboard 点击路径；
- 需要选择或填写的准确非秘密值；
- **哪些内容绝不能粘贴到聊天**；
- UI 中怎样算完成；
- 人回来以后 Agent 会验证什么；
- rollback / correction 路径。

默认 Workers Builds Native Profile 的权威人工指南是固定版本 PPF：

`docs/PER_PROJECT_GITHUB_CLOUDFLARE_SETUP.zh-CN.md`

Starter 的验收契约是：

`docs/PROJECT_PROVISIONING_ACCEPTANCE.zh-CN.md`

如果 Provider UI 变化，应先依据当前官方 Provider 文档更新仓库指南，再指导人类操作；不得只在聊天里临时修正流程。

## 5. 默认 Bootstrap 状态序列

普通 `workers-builds-native` 项目按以下状态推进：

```text
not-started
-> waiting-human / 必要时创建 repository
-> repository private verified
-> 复用或创建 Git account connection
-> 必要时授权 repository access
-> Workers Builds connected
-> Worker name alignment verified
-> Zero Trust verified（或完成一次性 setup）
-> Worker Access verified-private
-> first-deployment-verified
-> second-push-auto-deploy verified
-> operationally-verified
```

任何阶段失败都写为 `blocked`，并在 Task Plan 记录下一步 repair action。

## 6. 状态归属必须清楚

| 事实 | 持久权威 |
| --- | --- |
| 预期 deployment profile / privacy / Access mode | `project-provisioning.yaml` |
| 实际 repository / Workers Builds / Access / deployment 状态 | `project-bootstrap-state.yaml` |
| 当前 blocker 与下一步人类 / Agent 动作 | AHICP Current Focus + Task Plan |
| 里程碑历史 | AHICP Work Log |
| 持久的人类政策 / publication 决定 | AHICP Decision Log / appropriate Core |
| Secret value / token / OTP / recovery code | **永不进入仓库或聊天** |

Provider Dashboard 仍是外部系统真实状态；仓库保存的是最近一次已验证的非秘密投影。

## 7. Secret 边界

Bootstrap State 可以记录：

- repository URL；
- Worker URL；
- 非秘密 Provider ID；
- source revision；
- verification result；
- Access application reference；
- rollback / version reference。

不得记录：

- password；
- API token value；
- OAuth code；
- private key；
- OTP；
- recovery code；
- reader credential；
- session cookie。

Schema 固定要求 `secret_material: forbidden`。

## 8. 零上下文接管要求

新的 Agent 不得根据旧聊天恢复基础设施状态。

完整栈项目在正常 AHICP Working Memory 读取以后，还应读取：

- `project-stack.yaml`；
- `project-provisioning.yaml`；
- `project-bootstrap-state.yaml`；
- 当前任务涉及 Provider 时，读取固定版本 PPF 的每项目人工操作指南。

如果仓库记录与 Provider actual state 不一致，先记录 synchronization defect 并 reconciliation，再做新的 mutating work。

## 9. 完成条件

只有同时满足以下条件，项目才可以标记为 operationally verified：

- `project-bootstrap-state.yaml.status == operationally-verified`；
- repository privacy 已验证；
- Workers Builds repository connection 已验证；
- Worker name alignment 已验证；
- Access 已 verified private；
- 第一次 deployment 已验证；
- 第二次 push 无需重新授权即可自动部署；
- 项目记忆 write-back 已 synchronized；
- public release 仍为 not authorized，除非后续另有人类明确决定改变它。

完成状态必须在仓库里，不能只存在于 Agent 记忆中。
