# Cloudflare 最小人类操作交接

**状态：** 默认每项目 private/restricted Continuous Web 的权威操作交接  
**新项目默认 Infrastructure Profile：** `workers-builds-native`  
**默认配置模式：** `human-assisted-once-per-project`

本指南定义普通新项目所需的最少现实人工操作。

目标不再是“账户只授权一次，以后任何项目完全不碰 UI”，而是：

> **每项目一次短 bootstrap，之后普通 push 自动部署。**

完整编排规则见 [PROJECT_PROVISIONING_CONTRACT.zh-CN.md](PROJECT_PROVISIONING_CONTRACT.zh-CN.md)。真正可执行的 Provider implementation 仍由 PPF 负责。

## 1. 默认项目模型

```text
ChongLiuPhil 个人账号下 private GitHub repository
-> 每项目一次 Cloudflare Git repository connection
-> Workers Builds
-> Worker-scoped Cloudflare Access
-> 第一次 restricted deployment
-> 第二次 push 验证自动重新部署
```

Account-wide Access 与账户级 Provisioning automation 都属于可选优化，不是前置条件。

## 2. 正常的人类角色

每个新项目，人类可能需要：

1. 创建或确认 private GitHub repository；
2. GitHub 提示时，批准 Cloudflare Git 访问该 repository；
3. 在 Cloudflare Workers & Pages 选择并连接 repository；
4. 确认 production branch / build settings；
5. 启用 Worker-scoped Cloudflare Access 并选择认证 policy；
6. 确认第一次 restricted deployment。

这些是体系允许存在的 project-level consent。

Agent 应在这些步骤前后继续完成所有可以独立自动完成的技术工作。

## 3. 默认准确值

以固定版本 Project / PPF contract 为真值源。

普通参考值：

```text
GitHub owner: ChongLiuPhil
repository visibility: private
production branch: main
Cloudflare profile: workers-builds-native
root directory: /
build command: bash scripts/cloudflare_build.sh
deploy command: npx wrangler deploy
preview/non-production builds: disabled
Access mode: worker-scoped-access
public release: not authorized
```

如果当前 Provider UI 不同，先核对当前官方文档与实际 Provider state，不得猜。

## 4. Repository Connection

在 Cloudflare Workers & Pages：

1. 选择 **Create application** / repository import；
2. 选择目标 GitHub repository；
3. 如果 repository 不可见，管理 Cloudflare GitHub App installation，并给当前 repository access；
4. 配置固定 build / deploy 值；
5. Save / Deploy。

条件允许时优先使用 repository-scoped GitHub App access。

默认 Profile 不需要把 Cloudflare deployment token 粘贴到聊天。

## 5. Worker Access

Worker 创建后：

1. 打开该 Worker；
2. 打开 **Access**；
3. 选择 **Protect this Worker behind Access**；
4. 选择 **All traffic**；
5. 选择/创建批准的认证 policy；
6. Apply。

如果已验证的 account-wide **Protect all Workers** 已覆盖目标 Worker，则记录真实模式，不需要重复建 policy。

匿名请求没有真实被 challenge / deny 前，不得声称 private readiness。

## 6. 第一次 Deployment 验证

核验：

- repository 仍为 private；
- Cloudflare 指向正确 repository；
- production branch 为 `main`；
- deployed source revision 正确；
- 匿名 production access 被 deny/challenge；
- 已批准认证访问成功；
- direct asset URL 不能绕过 Access；
- Git/chat/log 中没有 secret value。

## 7. 第二次 Push 验证

对 source 做一次无害修改并 push 到 `main`。

只有以下成立才通过：

```text
push
-> Workers Builds 自动启动
-> 新 revision 部署
-> Access 继续生效
-> 不需要重新 GitHub / Cloudflare authorization
```

这一步证明每项目 bootstrap 真正完成。

## 8. 始终保留给人的决定

以下动作始终返回人类：

- Web 公开发布；
- source repository 公开；
- reader audience 扩大；
- Custom Domain / DNS 变化；
- Provider permission 扩大；
- paid plan / billing 变化。

## 9. 可选高级 Profile

项目明确选择 `agent-provisioned-external-ci` 时，改为遵循高级 PPF runbook。该路径使用 Platform Authorization、GitHub Actions、individual-Worker `Editor` token 与 Trusted Secret Broker。

没有明确 migration plan 时，不得混用两种 Profile。

## 10. 完成门

默认配置只有在以下全部成立时才完成：

- private source identity 正确；
- Workers Builds repository connection verified；
- target Worker 正确；
- Access 已 verified private；
- 第一次 restricted deployment verified；
- 第二次 push 无需重新授权即可自动部署；
- rollback / restore 明确；
- 只写回非秘密 Provider state；
- public release 继续未授权。
