# Continuous Web 与 Cloudflare 操作指南

新项目先读 [PROJECT_PROVISIONING_CONTRACT.zh-CN.md](PROJECT_PROVISIONING_CONTRACT.zh-CN.md)，再读 [CLOUDFLARE_MINIMAL_HUMAN_HANDOFF.zh-CN.md](CLOUDFLARE_MINIMAL_HUMAN_HANDOFF.zh-CN.md)。如交给可操作浏览器的 Agent，使用 [CLOUDFLARE_WORK_AGENT_HANDOFF.zh-CN.md](CLOUDFLARE_WORK_AGENT_HANDOFF.zh-CN.md)。非秘密机器计划见 [../templates/cloudflare-access-plan.yaml](../templates/cloudflare-access-plan.yaml)。

本指南是一份可复用的操作契约，不表示所有项目已经完成部署。

## 1. 分开四个层次

~~~text
私人源仓库
    -> 验证与构建
    -> Cloudflare 部署
    -> 读者访问策略
~~~

必须分别决定：

- 源文件隐私：canonical 源文件与原创作品是否 private；
- 部署身份：哪些凭据可以构建或部署；
- 读者访问：哪些人可以阅读已部署 Web；
- 搜索可见性：搜索引擎是否可以索引。

改变其中一层不得静默改变其他层。尤其是 Web 公开并不要求 canonical GitHub 仓库也公开。

## 2. 私人项目默认姿态

对于未发布、研究、手稿或其他具有版权属性的作品：

1. canonical 源仓库保持 private；
2. 除非人类明确选择精简 profile，否则保持完整 AHICP 和完整 PPF active；
3. 使用 private CI 或 Cloudflare 侧 Git 集成，不把源文件复制到公共仓库；
4. 只部署有意输出的渲染产物；
5. 在明确得到公开发布授权之前，Web 保持 restricted；
6. 使用 Cloudflare Access 或等效服务端访问门进行读者认证；
7. 项目文件只保存 access-policy reference，不保存真实密码、token、私钥、恢复码或其他秘密；
8. 对 restricted 内容关闭索引，并验证 preview、静态资源、feed、生成文件与备用 hostname 都遵守同一访问策略。

统一阅读凭据可以作为临时政策，但它本质上是共享秘密，秘密值必须留在 provider 侧。项目敏感度或读者规模增加后，应优先采用统一管理、短期或可单独撤销的凭据。

## 3. 声明式项目状态

新的私人项目通常应从等价于以下状态开始：

~~~yaml
source:
  visibility: private

publication:
  web:
    mode: continuous
    enabled: true
    authorization_state: not-authorized
    visibility: restricted
    access:
      mode: authenticated
      implementation: cloudflare-access
      policy_ref: shared-reader-access

deployment:
  web:
    provider: cloudflare-workers
    enabled: false
    status: staged
~~~

policy_ref 只用于标识预期策略，绝不能用来存放真实凭据。

## 4. 部署 Profile

部署前必须选择并记录一种 Profile：

- **Workers Builds Native + private-project-quota-saver — 普通新项目默认。** 允许使用者每项目完成一次短 GitHub ↔ Cloudflare connection；之后 Git-triggered production build/deploy 与 Provider-managed build credential 由 Cloudflare 负责。Content-only 改动不启动 GitHub Actions，配置 PR 只运行一个轻量 contract check，main push 不在 GitHub Actions 重复 Web build，heavy GitHub validation 手动运行。
- **Agent-Provisioned External CI — 高级可选 Profile。** 只有项目明确需要 account-owned individual-Worker `Editor` deployment credential、可复用 Platform Authorization 与 Trusted Secret Broker 时采用。
- **未来 / Provider-specific Profile** — 只有当前官方文档和真实测试确认支持后才能采用。

默认 Profile 优先追求现实可用、配置简单，而不是把账户级零人工 Provisioning 当作前置条件。Deployment credential scope 与 reader access 仍是两个独立安全轴。

## 5. 必要配置顺序

普通新项目：

1. 确认准确的个人 GitHub repository、output directory、Cloudflare account 与目标 Worker/project。
2. 确认 source repository 为 private。
3. 除非人类明确选择高级 Profile，否则使用 `workers-builds-native` + `private-project-quota-saver`。
4. 在 `ChongLiuPhil` 下创建或确认 private repository。
5. 在 Cloudflare Workers & Pages 中 Import / Connect 该 repository。
6. 如果 GitHub 提示，为目标 repository 授权 Cloudflare Git integration。
7. 配置 production branch `main`、root `/`、`bash scripts/cloudflare_build.sh` 与 `npx wrangler deploy`。
8. Preview / non-production build 默认关闭。
9. 完成第一次 deployment。
10. 给 Worker 启用 Worker-scoped Cloudflare Access，选择 **All traffic**；如果已有 verified account-wide Access 覆盖，则记录并复用。
11. 验证 deployed revision、匿名 challenge / deny、已授权 reader 与代表性 direct asset。
12. 对 source 做一次无害的 content-only 修改并 push 到 `main`。
13. 确认 Workers Builds 自动部署新 revision，不需要重新 GitHub / Cloudflare authorization，而且没有启动重复的 GitHub Actions production Web build。
14. Custom Domain 只有另行获得 domain/DNS authorization 后才配置。
15. 记录已验证的非秘密 Provider state 与 rollback evidence。

如果显式选择高级 External-CI Profile，则改为遵循固定版本 PPF 的 External-CI / Trusted Secret Broker 契约。

## 6. AI Agent 必须采用的人类交接格式

凡 Cloudflare 操作需要人类账户所有者执行，Agent 都必须给出编号步骤，并包含：

1. **目标**：准确 account、project/Worker、repository、hostname/domain 和 environment；
2. **影响**：说明本步骤改变 deployment、DNS、routing、access、indexing，还是只读检查；
3. **点击路径**：当前 Dashboard 区域和 UI 导航路径；若记录可能过时，先核对当前 UI 或官方文档；
4. **填写内容**：来自项目配置的准确非秘密值；只有确实需要人类持有值时才使用占位说明；
5. **秘密边界**：明确哪些内容绝不能粘贴到聊天；
6. **完成证据**：人类完成后应看到什么成功状态；
7. **Agent 恢复点**：随后 Agent 将验证哪些 provider/repository 状态；
8. **回滚**：如果改变了 publication、access、DNS 或 routing，如何撤销。

仅说“配置 Cloudflare”“启用 Access”“设置 DNS”都不够。

## 7. GitHub + Cloudflare 项目集成

默认路线允许并预期“每项目一次 Cloudflare Git authorization”：当 Cloudflare GitHub App 尚未访问目标 repository 时，由使用者在 Provider UI 完成授权。

读取固定版本 PPF runbook：

- `docs/PER_PROJECT_GITHUB_CLOUDFLARE_SETUP.zh-CN.md`：默认每项目操作流程；
- `docs/CI_COST_POLICY.zh-CN.md`：private repository GitHub Actions / build-minute 策略；
- `docs/CLOUDFLARE_GITHUB_AUTHORIZATION.zh-CN.md`：Native 默认与高级可选授权模型；
- `docs/CLOUDFLARE_SECURITY_PROFILES.zh-CN.md`：deployment credential 权衡；
- `docs/CLOUDFLARE_ACCESS_PROFILE.zh-CN.md`：publication visibility → reader access；
- `docs/AGENT_PROVISIONED_EXTERNAL_CI.zh-CN.md`：仅高级可选 Profile。

普通项目不得因为没有账户级 Provisioning 就被阻塞；也不得因为 repository connection 需要人工 consent 就放宽项目隐私。

## 8. Restricted reader access 配置

在 restricted publication 被视为安全之前：

1. 确认需要保护的 hostname 或 route；
2. 创建或选择针对该 hostname 的 access application/policy；
3. 选择预期 authentication mechanism 或 audience rule；
4. 将相同策略覆盖到 production 以及可能暴露相同内容的 preview/alternate route；
5. 任何统一阅读凭据或身份秘密都必须完全留在 Git 与 chat 之外；
6. 使用新的 private/incognito session 作为未认证读者测试：必须被拒绝或要求认证；
7. 使用授权身份测试：必须可以正常访问；
8. 未认证状态下直接请求一个已知 asset、feed 或生成文件 URL，确认不存在绕过；
9. 确认 restricted 页面不被有意开放索引；
10. 只把非秘密 policy reference 和验证结果写回私人项目状态。

## 9. 转为 Public

从 restricted 转为 public 是发布决定，不只是技术开关。

切换前：

1. 确认得到人类明确公开发布授权；
2. 验证渲染输出只包含已批准公开材料；
3. 验证私人 working memory、credentials、未发布 assets 与仅源文件内容未进入输出；
4. 更新 access policy；
5. 测试匿名访问；
6. 按预期验证 search/canonical behavior；
7. 记录新的 publication state。

源 GitHub 仓库仍可继续保持 private。

## 10. 秘密与凭据处理

Agent 绝不能要求人类把密码、API token、私钥、恢复码或其他凭据发送到聊天。

如果 provider UI 必须输入秘密：

1. 明确告诉人类是哪个 provider 字段需要该秘密；
2. 要求人类只在 provider UI 中直接输入；
3. 明确说明不要把值发回 AI；
4. 之后只验证非秘密的结果状态。

## 11. 完成门

Continuous Web 只有在以下条件全部满足时才算配置完成：

- 仓库 validation/build gate 通过；
- deployed URL 在预期 policy 下可访问；
- restricted 内容不能匿名读取；
- public 内容没有被意外限制；
- direct assets 与 alternate routes 不能绕过 access control；
- production authorization state 正确；
- rollback 路径明确；
- 已验证 provider state 已写回私人项目记录。
