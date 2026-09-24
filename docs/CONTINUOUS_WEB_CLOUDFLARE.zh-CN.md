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

## 4. 部署 profile

部署前必须选择并记录一种 Profile：

- **Agent-Provisioned External CI — 平台 bootstrap 后新项目首选。** Platform Provisioner 创建 Worker；trusted broker 把只限制到该 individual Worker、角色为 Editor 的 account-owned token 直接写入 GitHub Actions；token 明文不进入模型。
- **Workers Builds Native — provider-native 备选。** 明确重视原生 Git integration 或已有采用时使用；当前 build credential 使用 Provider user-token 模型。
- **未来/Provider-specific Profile** — 只有当前文档与真实测试确认支持后才能采用。

PPF 的安全 profile 文档记录参考权衡。部署凭据安全与读者访问控制仍然是两个正交安全轴。

## 5. 必要配置顺序

1. 确认准确的 GitHub 源仓库、输出目录、canonical domain、可见性、保留策略、Cloudflare account 与目标 Worker/project。
2. 如果项目含有未发布原创内容，确认源仓库为 private。
3. 选择 build/deployment Profile；新项目除非明确选择其他 Profile，否则采用 `agent-provisioned-external-ci`。
4. 创建 Worker 前先验证 platform standing authorization 与 account-wide `all_workers` Access。
5. 通过已授权 Provisioner 创建/复用 private GitHub repository 与 restricted Worker。
6. External CI 由 trusted Secret Broker 把 project-scoped Worker credential 直接安装到 GitHub Actions；明文不得暴露给 Agent。
7. 根据 repository machine contract 配置 build command 与 output path。
8. Preview 在独立保护验收前保持 disabled。
9. 只有 durable project authorization 覆盖 restricted Web deployment 时才部署 restricted production。
10. 验证准确 deployed revision、anonymous denial 与代表性 direct asset。
11. Custom Domain 只有独立 domain/DNS authorization 后才配置。
12. 把已验证的非秘密 Provider state、deployment revision、access-policy reference 与 rollback result 写回 private project state。

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

## 7. GitHub + Cloudflare 平台集成

首选新项目路径不需要 per-project Cloudflare GitHub App authorization。Starter 校验 platform authorization，并把 Provider execution 交给固定版本 PPF 的 `agent-provisioned-external-ci` 实现。

读取当前 PPF runbook：

- docs/AGENT_PROVISIONED_EXTERNAL_CI.zh-CN.md：最小人类新项目 Profile；
- docs/CLOUDFLARE_GITHUB_AUTHORIZATION.zh-CN.md：两项平台级授权与 Native 备选；
- docs/CLOUDFLARE_SECURITY_PROFILES.zh-CN.md：Provisioning / deployment credential 边界；
- docs/CLOUDFLARE_ACCESS_PROFILE.zh-CN.md：publication visibility → reader access；
- docs/CLOUDFLARE_OBSERVED_UI_MAPPING.zh-CN.md：带日期 UI 观察。

只有明确选择 `workers-builds-native` 时才走 Cloudflare GitHub App 授权；不得因为旧习惯对 External-CI 项目套用该步骤。

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
