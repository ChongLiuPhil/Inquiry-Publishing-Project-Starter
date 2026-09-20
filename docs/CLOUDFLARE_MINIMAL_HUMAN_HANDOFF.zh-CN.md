# Cloudflare 最小人类操作交接

**状态：** private/restricted Continuous Web 的 canonical 操作交接  
**策略引用：** `shared-reader-access`

本指南把 Cloudflare 配置压缩到尽可能少的人类保留操作。其余工作应尽量由获得授权的 API Agent，或可使用浏览器的 ChatGPT Work 类 Agent 完成。

## 1. Canonical 访问模型

Canonical 策略**不是仓库密码**，而是一个名为 `shared-reader-access` 的可复用 Cloudflare Access policy。

对人类读者，当前推荐的低摩擦模型是：

~~~text
restricted hostname
-> Cloudflare Access
-> shared-reader-access reusable policy
-> 明确允许的读者 email
-> One-Time PIN
-> 24h session
~~~

共享的是 policy 名称；读者身份、Cloudflare application/policy ID 与其他 provider state 保持在私人 provider state 中。

Cloudflare Access 当前官方模型以身份与策略为中心，并没有通用的“静态共享密码” Access selector。因此，已经存在的统一阅读密码应当视为**旧系统兼容凭据**，而不是新的 canonical Access 机制。不要为了保留旧体验而把密码移入 Git。

## 2. 应当保留给人类的最少操作

正常情况下，人类只需要做：

1. 登录 Cloudflare 并完成 MFA。
2. **每个 GitHub account/org 一次：** 授权 Cloudflare Workers & Pages GitHub App 访问指定仓库。
3. **每个 automation principal 一次：** 创建初始 scoped API token。Token 只进入执行 Agent 的安全 secret store，绝不粘贴进聊天或 Git。
4. 确认实际允许阅读的人。使用 OTP 时，把读者 email 直接填入 Cloudflare 或安全 Agent 表单。
5. 如果旧部署仍使用统一静态密码，由人类把该秘密直接输入现有 provider-side secret 字段；不要把值发送给 AI。
6. 将来如果要从 restricted 变为 public，由人类明确批准最终公开发布。

其余步骤都应尽量由 Agent 完成并验证。

## 3. 一次性 Cloudflare ↔ GitHub 授权

当前 Workers Builds 的人类操作：

1. Cloudflare Dashboard → **Workers & Pages**。
2. 打开目标 Worker → **Settings → Builds → Connect**。
3. 选择 **GitHub**。
4. 安装/授权 **Cloudflare Workers and Pages** GitHub App。
5. 优先选择 **selected repositories only**，只授权实际需要构建的项目仓库。
6. 返回 Cloudflare，确认 Worker 的 Build settings 已显示目标 Git repository。

这是最主要的不可替代账户所有者授权。完成以后，Workers Builds 的触发器与配置可以通过 Cloudflare Builds API 自动化。

## 4. 一次性 API 自动化凭据

如果后续交给 API Agent，在 **My Profile → API Tokens → Create Token → Custom token** 创建最小权限 user token。

### Access application / policy token

权限：

~~~text
Account → Access: Apps and Policies → Edit
~~~

尽可能把资源范围限制到目标 Cloudflare account。

### Identity provider token

只有 Agent 需要创建或修改 OTP/IdP 时才授予：

~~~text
Account → Access: Organizations, Identity Providers, and Groups → Edit
~~~

如果 OTP/IdP 已经存在，就不要增加这项权限。

### Workers Builds token

Cloudflare 当前 Builds API 要求 **user-scoped** API token：

~~~text
Account → Workers Builds Configuration → Edit
Account → Workers Scripts → Read
~~~

前者用于 build trigger/configuration；后者只用于解析 Worker 的 immutable tag。

不要使用 Global API key。

## 5. 读者认证：推荐 OTP 路径

如果 One-Time PIN 尚未存在：

1. Cloudflare Dashboard → **Zero Trust → Integrations → Identity providers**。
2. 在 **Your identity providers** 下选择 **Add new identity provider**。
3. 选择 **One-time PIN**。
4. Save。
5. 不要为了省事创建 `Everyone` 或“所有有效 email”式 Allow policy。

建立 reusable policy：

1. **Zero Trust → Access controls → Policies**。
2. 选择 **Add a policy**。
3. Policy name：`shared-reader-access`。
4. Action：**Allow**。
5. Session duration：初始使用 **24 hours**。
6. Include：**Emails** → 只加入获准读者 email。
7. Require：**Login Methods** → **One-time PIN**。
8. Save。

24 小时只是当前安全性/便利性的初始平衡；将来修改 session 是策略决定，不是模板迁移。

## 6. 保护一个 publication hostname

每个 restricted publication：

1. **Zero Trust → Access controls → Applications**。
2. **Create new application**。
3. 选择 **Self-hosted and private**。
4. **Add public hostname**。
5. 填入项目 canonical restricted hostname。除非项目契约明确要求更窄 path，否则保护整个 hostname。
6. **Access policies** 中附加已有 reusable policy `shared-reader-access`。
7. 选择预期 login provider，通常为 One-Time PIN。
8. Application session duration 初始同样用 24 hours。
9. Save。
10. 在暴露未发布输出之前，确认准确 hostname 已存在对应 Access application。

受 Access 保护的 application 默认拒绝未匹配 Allow policy 的请求。

## 7. 人类 bootstrap 之后由 Agent 完成

GitHub App 与 scoped API token 就绪后，API Agent 应完成：

1. 读取项目 `publishing.yaml`、`cloudflare-builds.yaml`、Worker name、repository ID、branch、build/deploy/preview command 与 hostname。
2. 读取 Cloudflare actual state。
3. 通过 Access API 创建或更新 `shared-reader-access`。
4. 创建或更新对应 hostname 的 self-hosted Access application。
5. 在 GitHub App 已授权前提下配置 Workers Builds。
6. 触发 preview build。
7. 验证 build revision、runtime URL、Access 行为、direct asset、feed 与 alternate route。
8. 只把非秘密 ID/status 写回私人 project state。
9. 没有人类明确 public-release authorization 时，在公开切换前停止。

## 8. Browser Agent / ChatGPT Work

没有直接 Cloudflare API 工具时，使用 **Work mode**，并采用 `CLOUDFLARE_WORK_AGENT_HANDOFF.zh-CN.md` 中的 prompt。

只有出现以下界面时交还人类：

- Cloudflare 登录/MFA；
- GitHub App authorization；
- API token secret 的生成与安全保存；
- 读者 identity 批准；
- 旧统一密码/秘密的直接输入；
- 最终公开发布批准。

人类完成后立即把控制权交回 Agent，让 Agent 继续设置与验证。

## 9. 旧统一静态阅读密码

如果当前部署已经有一个共享静态阅读密码：

- **不要发送到聊天**；
- **不要写进** `publishing.yaml`、`website.yaml`、`wrangler.jsonc`、Git-tracked CI config 或 Access policy metadata；
- 如果既有 runtime 已有 provider-side secret 字段，人类可以直接把当前值填进去，作为临时 compatibility layer；
- 除非“必须保持完全相同的单一密码 UX”是明确项目需求，否则不要为了新项目再造一个静态密码 gate；
- 对人类读者优先迁移到 Access identity + OTP，同时继续把 `shared-reader-access` 作为稳定 policy reference。

## 10. 完成验证门

restricted Continuous Web 只有在全部满足时才完成：

- private/incognito 匿名访问被 challenge 或 deny；
- approved reader 可以认证阅读；
- unapproved reader 不能阅读；
- direct asset/feed/generated-file URL 不能绕过 Access；
- preview 与 production endpoint 符合预期保护策略；
- deployed revision 与目标 source revision 一致；
- Git、build log、PR、chat 中不存在 reader secret；
- rollback 路径明确；
- 私人 project state 记录 Access application ID / policy ID 与验证结果，但不记录 credential value。
