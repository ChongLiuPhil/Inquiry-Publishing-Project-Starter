# Cloudflare 公共站点迁移

**状态：** 仓库侧迁移准备已建立；仍需要 Cloudflare 账户授权。

## 目标

把四个公共框架网站从 GitHub Pages 迁移到 **Cloudflare Pages**，同时继续把 GitHub 作为权威源文件、版本历史、审阅和 CI 平台。

四个站点包括：

- AHICP 公共介绍页 / Human Entry；
- PPF 公共主页；
- Vault Interface 公共主页；
- Starter 公共主页，以及稳定的 `/agent/` 机器入口。

这次迁移不会改变 AHICP、PPF、Vault Interface 和 Starter 各自的规范权威。

## 为什么选择 Cloudflare Pages

目前四个站点都是从各仓库的 `docs/` 目录直接提供静态内容，因此 Cloudflare Pages 是更合适的默认交付方式：

- 可以直接连接 GitHub 自动部署生产版本；
- 分支和 Pull Request 可以生成预览部署；
- 预览可以通过 Cloudflare Access 限制访问；
- 可以使用自定义域名，让公共身份不再绑定某个托管平台；
- 当前静态站点不需要额外引入 Worker 运行时。

只有真正需要运行时逻辑时才使用 Workers。不要因为 Workers 可用，就把纯静态框架网站搬到 Workers。

## 当前状态与目标状态

当前：

~~~text
GitHub repository
  -> GitHub Pages
  -> chongliuphil.github.io/... 公共 URL
~~~

目标：

~~~text
GitHub repository（权威源）
  -> Cloudflare Pages（网页交付）
  -> 自定义域名（稳定公共身份）
~~~

在 Cloudflare 部署完成并验证以前，GitHub Pages 继续作为当前正式公共入口。`*.pages.dev` 可以用于 staging，但在可以使用自定义域名时，不应把它作为体系的永久身份。

机器可读迁移计划见 [`templates/cloudflare-public-delivery.yaml`](../templates/cloudflare-public-delivery.yaml)。

## 四个站点的默认 Pages 构建设置

~~~text
Production branch: main
Root directory: .
Build command: exit 0
Build output directory: docs
Framework preset: none
~~~

当前四个站点都不需要框架构建步骤；Cloudflare 直接部署仓库中已有的 `docs/` 内容。

## 预览策略

预览部署有价值，但不应该意外变成新的公开发布面。

默认：

~~~text
preview deployments: enabled
preview visibility: restricted
access layer: Cloudflare Access
production framework sites: public
~~~

这里说的是这四个已经公开的框架网站。下游原创或未发布项目仍然遵循另一套默认：生产 Web 在明确公开授权前保持 restricted + authenticated。

## 必须由人完成的一次性操作

当前 Agent 环境没有经过认证的 Cloudflare 控制平面，因此账户所有者需要完成 provider bootstrap：

1. 登录 Cloudflare，并完成 MFA。
2. 授权 Cloudflare Workers & Pages GitHub App 访问这四个仓库。优先选择 **selected repositories only**。
3. 为四个仓库分别创建/导入 Cloudflare Pages project，使用上面的统一构建设置。
4. 记录每个 project name 和生成的 `*.pages.dev` staging URL。
5. 决定稳定的自定义域名布局；这一步完成前不要修改 ecosystem 中的正式公共 URL。
6. 如果域名/zone 尚未进入 Cloudflare，完成必要的 DNS / zone 授权。
7. 把**非秘密**的 project name、staging URL 和 custom-domain URL 告诉 Agent。不要把 API token、密码、私钥、恢复码或其他秘密发送到聊天。

这些门槛完成后，获得授权的 Agent 应在工具允许时继续完成验证和元数据切换。

## 切换前验证

在以下条件全部满足前，不修改任何当前公共入口：

- 四个 Cloudflare production deployment 都对应预期的 `main` revision；
- 四个主页均能正常加载；
- AHICP 仍然完整提供 Human Entry 和最终启动动作；
- Starter 的 `/agent/`、`/agent/entry.json`、bootstrap 文件和 `llms.txt` 在目标域名上正常解析；
- 四个站点之间的交叉链接正常；
- preview deployment 按预期被限制访问；
- Git、PR、build log 和 chat 中没有秘密；
- 已经明确如何退回当前 GitHub Pages URL。

## 原子化切换公共 URL

Cloudflare 目标和自定义域名完成验证以后，再通过一次协调变更同时更新：

- GitHub About Website；
- 四个 `ecosystem.yaml`；
- 四个 `docs/llms.txt`；
- Starter `docs/agent/entry.json`；
- Starter Agent Retrieval Contract；
- 四站点之间的主页链接；
- README 中代表公共入口的 URL。

GitHub 仓库作为权威源的 URL 不变。

## 迁移期间怎样处理 GitHub Pages

Cloudflare 切换验证完成以前，不关闭 GitHub Pages。

切换前，GitHub Pages 是生产 fallback。

切换后，可以暂时保留 GitHub Pages 作为回滚路径；是否关闭或做重定向属于后续清理动作，不应和第一次 Cloudflare 验证混在一起。

## 回滚

公共 URL 尚未切换时，回滚就是继续使用现有 GitHub Pages，不需要额外动作。

公共 URL 已经切换以后，回滚就是恢复之前的公共 URL / DNS 和 ecosystem 元数据。紧急回滚时不要顺手删除 Cloudflare project，应保留现场用于诊断。
