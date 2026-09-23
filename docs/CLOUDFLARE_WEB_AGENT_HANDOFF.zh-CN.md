# Web AI Agent 接续：GitHub 与 Cloudflare

本交接基于 2026-09-23 已验收的 Worker 正式 URL 切换。接手时先读取[机器入口](https://inquirystack.philohub.workers.dev/agent/)、Starter 当前 `main` 的 `AGENTS.md`、`ecosystem.yaml`、Agent Retrieval Contract、[迁移契约](CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.zh-CN.md)、[实际验收记录](CLOUDFLARE_DEPLOYMENT_ACCEPTANCE.zh-CN.md)、`cloudflare-builds.yaml`、`wrangler.jsonc` 与 `site/sources.lock.json`。再核对 GitHub 当前 revision、线上 `/build-info.json` 和 Cloudflare 当前部署；历史 SHA 是证据，不是最新状态保证。不需要原电脑或本地附件。

## 当前可依赖的事实

- 四个独立仓库组成一个公开网站；Worker 为 `inquirystack`，账户前缀 `philohub`，地址 `https://inquirystack.philohub.workers.dev/`。`/` 为人类入口，`/agent/` 为机器入口。
- 只把 Starter 连接到原生 Workers Builds。主分支 `main`、根目录 `/`、输出 `_site`；完整构建和主站部署已实际通过。构建命令及工具版本以 `cloudflare-builds.yaml` 为准。
- GitHub App `Inquiry Publishing ChongLiuPhil` 已安装于 Starter、AHICP、PPF、Vault Interface 四个选定仓库。App 最大权限包括 Contents 读、Actions 写、Pull requests 写；实际临时令牌只选择 Starter，并按通知或创建 PR 的动作进一步收窄。App 私钥与 Webhook Secret 在 Cloudflare Worker Secrets，App ID 为运行时文本变量。不要把任何秘密或读者身份放进 Git、日志或聊天。
- 已真实验证 PPF 提交 → App 通知 → Starter 来源锁 PR → 三项普通 CI → 合并 → Cloudflare 原生构建 → 线上内容更新；同一通知重放未产生重复部署。准确 SHA、运行链接和回滚边界见[验收记录](CLOUDFLARE_DEPLOYMENT_ACCEPTANCE.zh-CN.md)及[来源锁 PR #35](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/pull/35)。没有每小时检查。
- 当前主站匿名公开阅读及 `workers.dev` 正式身份已获用户批准；线上切换已通过验收并记录为 `verified-cutover`。预览 URL 与非主分支自动构建继续关闭；受限 Access 及读者身份验证仍未完成。原 GitHub Pages 和 Pages holding 保留；不改 DNS 或升级付费套餐。
- PPF 的通用生命周期工具 PR [#31](https://github.com/ChongLiuPhil/Personal-Publishing-Framework/pull/31) 已合并。其 CLI `apply` 使用配置好的 Wrangler；不要声称它自动协调 Cloudflare Builds 的 GitHub 连接/触发器。综合站现有连接是已实际配置并验证的实例，通用工具的能力边界仍以 PPF 当前 `main` 为准。

## 后续操作

1. 先读取实际 Worker、Builds、GitHub App、主站与预览状态，再补齐差异；不要重复创建项目、连接或触发器。仅已登记公开来源按固定 SHA 发布，新的书籍或应用须先登记发布范围。
2. 每次上游更新核对来源锁、三项 PR 检查、Starter merge SHA、Cloudflare 构建以及线上 `/build-info.json`。成品不变则不提交来源锁、不重复部署；失败保留上一成功版本并报告具体阶段。
3. 若以后启用预览，先取得预览读者批准，配置并验证 `preview_worker` Access，包括匿名拒绝、获准读者可读、直接资源无绕过，再启用真实版本预览与非主分支构建。当前不能把此门记为通过。
4. 回滚前先读当前部署。通过正常 PR revert 来源锁，或恢复私有状态中上一已验证 Worker 版本，然后复核响应。保留旧站与历史 Pages holding；不强推、不删除项目。

常规配置与验证、所选 `workers.dev` 正式切换已获授权。只有登录/MFA、新增 GitHub App 授权、读者身份批准、其他域名或 DNS 授权、秘密直接输入及未来再次改变公开身份时才交还用户；届时给出确切链接与步骤。不得因当前主站公开而使预览或其他项目公开。
