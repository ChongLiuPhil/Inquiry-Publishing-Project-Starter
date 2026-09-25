# 项目 Provisioning 契约

**状态：** Starter 新项目编排的权威契约  
**默认基础设施 Profile：** `workers-builds-native`  
**默认配置模式：** `human-assisted-once-per-project`  
**默认 CI 成本 Profile：** `private-project-quota-saver`

本契约定义 Inquiry Publishing Stack 当前实际采用的新项目路径。

默认路线**不再假定账户级零人工 Provisioning 已经建立**。每个项目明确允许一次少量 GitHub / Cloudflare 人工配置；该项目 bootstrap 完成后，普通 source push 应自动构建并部署。

`agent-provisioned-external-ci` + Trusted Secret Broker 继续作为项目明确选择时使用的高级可选路线。

## 1. 默认目标

普通新项目的目标流程：

```text
人提出项目请求
-> ChongLiuPhil 个人账号下 private repository
-> 完整 AHICP + 完整 PPF + Vault Interface
-> project infrastructure manifest
-> 每项目一次 Cloudflare Git repository connection
-> Workers Builds
-> Worker-scoped Cloudflare Access
-> 验证第一次 restricted deployment
-> 第二次 push 无需重新授权
-> 后续普通 push 自动部署
```

实际承诺是：

> **每个项目只做一次短而明确、有文档可照着完成的 bootstrap；之后普通 push 自动部署。**

它不再声称所有未来 repository 都能完全零人工创建并接入 Provider。

## 2. 默认 GitHub 拓扑

普通 downstream project 默认：

```yaml
github:
  owner: ChongLiuPhil
  owner_type: user
  visibility: private
```

使用者可以先在 GitHub 手动创建 repository，再由 Agent 配置。自动建仓属于优化，不是前置条件。

因此默认路线不要求 GitHub Organization，也不要求先建立账户级 Project Provisioner App。

新 repository 必须以 private 开始。改成 public 是另一项独立的人类保留决定。

## 3. 默认 Cloudflare 拓扑

默认 PPF infrastructure profile 与 CI cost profile：

```text
workers-builds-native
private-project-quota-saver
```

项目把 private GitHub repository 连接到 Cloudflare Workers Builds。之后 Git-triggered build/deploy connection 与 build credential 由 Cloudflare 管理。

参考配置：

```text
Worker / application name: 必须与 wrangler.jsonc.name 完全一致
production branch: main
root directory: /
build command: bash scripts/cloudflare_build.sh
deploy command: npx wrangler deploy
preview / non-production builds: 默认关闭
```

如果 Git account 已经连接到 Cloudflare，直接复用该 account connection；不能仅因为新建了项目就机械地重新 OAuth。如果 private repository 不可见，条件允许时只为目标 repository 批准或扩大 Cloudflare GitHub App 的 repository access。

Provider UI 可能变化。Agent 必须根据当前 Provider state 与固定版本 PPF setup contract 行动，不得照旧截图猜字段。

### Private 项目 CI 成本默认

固定版本 PPF 的 `private-project-quota-saver` 是默认项目状态的一部分：

- content-only 改动不启动 GitHub Actions；
- 配置/基础设施 Pull Request 只运行一个轻量 contract check；
- push 到 `main` 不再运行重复的 GitHub Actions Web build；
- full Web validation、Cloudflare contract validation、publication artifact 与高级 External-CI deployment 都改为手动；
- Cloudflare Workers Builds 是唯一自动 production Web build；
- Cloudflare non-production build 与 Preview 默认关闭。

Agent 必须先批量完成相关编辑、运行所有可用 Agent-side preflight、检查完整 diff，然后只触发预定的薄 CI。不得把 GitHub Actions 当作迭代调试循环。Private repository Actions quota 已耗尽时，可选/手动 GitHub heavy validation 延后；除非人类明确授权，不得通过开启付费 usage 来绕过 quota。

## 4. 每项目一次人工 Bootstrap

正常情况下，人类可能需要完成：

1. 创建或确认个人账号下的 private GitHub repository；
2. 如果已有正常工作的 Cloudflare Git-account connection，直接复用；
3. 如果目标 private repository 不可见，只为该 repository 批准或扩大 Cloudflare GitHub App 的 repository access；
4. 把 repository 连接到 Workers Builds，并让 Worker / application name 与 `wrangler.jsonc.name` 完全一致；
5. 确认 production branch / build 配置；
6. 如果该 Cloudflare account 从未启用 Zero Trust，先完成这一次账户级前置 setup；之后项目直接复用；
7. 给目标 Worker 启用 Cloudflare Access，已有批准的 authentication policy 时优先复用；
8. 确认第一次 restricted deployment。

这些属于允许存在的项目级授权，不代表体系失败。

Agent 应继续完成所有不依赖人工 consent 的技术工作；只有 Provider UI / 账户所有者必须亲自完成的步骤才返回人类。

## 5. 私人 Web 默认值

新的未公开 Web output 默认：

```text
restricted + authenticated
```

普通 Access 模式：

```text
worker-scoped-access
```

如果账户已经存在并验证了 `all_workers` account-wide policy，也可以记录：

```text
account-wide-access
```

GitHub repository private 并不等于网页 private。Worker 本身必须受到 Access 保护，而且匿名访问必须真实被 challenge / deny。

Preview 默认关闭，直到 Preview protection 独立通过验证。

## 6. Project Request

新项目使用：

- `schema/project-provisioning-request.schema.json`
- `templates/project-provisioning-request.yaml`
- 根目录 `project-provisioning.yaml`

默认 Request 声明：

- `full-research-publication`；
- GitHub owner `ChongLiuPhil`；
- `owner_type: user`；
- private repository；
- `workers-builds-native`；
- `ci_cost_profile: private-project-quota-saver`；
- `access_mode: worker-scoped-access`；
- restricted Web；
- Preview disabled；
- 无 Custom Domain；
- `restricted_deployment_source: explicit-project-authorization`；
- `project_bootstrap: human-assisted-once-per-project`；
- `public_release: false`。

Request 不含 credential material。

## 7. Planner 语义

对默认 Native Profile，`platform-authorization.yaml` 保持 `unconfigured` **不会阻塞**项目规划。

默认 ready state：

```text
READY_FOR_PROJECT_BOOTSTRAP
```

生成的 PPF desired state 使用：

```text
provider: cloudflare-workers-builds
securityProfile: workers-builds-native
credentialStrategy: provider-managed-user-token
secretBroker: false
ciCostProfile: private-project-quota-saver
accessMode: worker-scoped-access
previewDeployments: false
```

只有项目显式选择高级 External-CI Profile 时，才要求 platform standing authorization。

## 8. 第一次配置后的验证

Cloudflare 显示首次 deployment success 还不够。

必须核验：

- GitHub repository 仍为 private；
- Cloudflare 连接到正确 repository；
- production branch 为 `main`；
- 部署的是预期 revision；
- Worker Access protection 已生效；
- 匿名 production 请求被 challenge / deny；
- 已批准 reader 完成认证后可以正常访问；
- direct asset 不能绕过 Access；
- Git、Issue、PR 文本、日志与 model/chat context 都没有 Provider credential value。

只记录非秘密 Provider state。

## 9. 第二次 Push 验收

第一次部署通过后，对 source 做一次无害修改并 push 到 `main`。

只有出现以下结果，项目才算 operationally verified：

```text
push
-> Workers Builds 自动启动
-> build 成功
-> 新 revision 成为 production
-> Access 继续生效
-> 不启动重复的 GitHub Actions production Web build
-> 不需要重新授权 GitHub 或 Cloudflare
```

这一步证明“一次项目 bootstrap”真正转化成了可持续复用的连接。

## 10. 人类保留 Gate

默认项目 bootstrap 永远不授权：

- Web restricted → public；
- source repository private → public / open source；
- reader audience 扩大；
- Custom Domain / DNS 变化；
- Provider permission scope 扩大；
- paid plan / billing 变化；
- 为绕过 quota 而开启付费 GitHub Actions usage、提高 Actions budget 或修改 billing。

这些仍由人明确决定。

## 11. Secret 边界

默认 Native Profile 不要求使用者把 Cloudflare deployment token 复制到 GitHub Actions，更不能粘贴到聊天。Workers Builds 使用 Provider 管理的 credential。

任何 Provider credential 都不得进入：

- Git；
- Starter / PPF YAML；
- Issue / PR body；
- 日志；
- chat / model context。

以后如果使用 API 自动管理 Provider，也必须让 credential 留在已授权的 Provider / tool boundary 内。

## 12. 可选高级 External-CI Profile

确实需要更强 deployment-credential isolation 的项目，可以显式选择：

```text
agent-provisioned-external-ci
```

高级 Profile 保留：

- reusable platform authorization；
- account-wide Access 前置条件；
- GitHub Actions deployment；
- account-owned individual-Worker `Editor` credential；
- Trusted Secret Broker 编排。

其 Cloudflare granular-token issuer 仍需 live Provider acceptance。高级 Profile 的未完成项不得被混入默认 Native 路线的完成标准。

## 13. 完成状态

默认项目 bootstrap 完成时，应能真实记录：

```text
github_repository: private
infrastructure_profile: workers-builds-native
ci_cost_profile: private-project-quota-saver
cloudflare_git_connection: verified
worker_access: verified-private
first_restricted_deployment: verified
second_push_auto_deploy: verified
public_release: NOT AUTHORIZED
```

Starter 负责组合与项目 bootstrap 编排；真正的 GitHub / Cloudflare 可执行 integration contract 与操作者步骤继续由 PPF 保持权威。
