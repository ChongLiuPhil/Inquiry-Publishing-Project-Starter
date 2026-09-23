# Cloudflare 单站 Workers 交付迁移

状态：完整公开候选站及 GitHub 提交触发更新已验收；用户已批准 `workers.dev` 正式 URL 切换，本次版本部署后仍须完成线上复核，才标记 verified-cutover。预览保持关闭，未通过 Access 验收。候选站版本与证据见[验收记录](CLOUDFLARE_DEPLOYMENT_ACCEPTANCE.zh-CN.md)。

## 已批准目标

四个仓库独立维护，组成一个网站，由 `inquirystack` Worker 提供服务，地址为 `https://inquirystack.philohub.workers.dev`。`/` 是人类入口，`/agent/` 是机器入口。GitHub 为权威源；只连接 Starter，其他三个公开上游按 `site/sources.lock.json` 固定 revision 无凭据读取。网站来源锁与下游采用锁分开维护。

用户已批准当前综合站主地址匿名公开阅读，并另行批准 `https://inquirystack.philohub.workers.dev/` 成为正式人类入口，`/agent/` 成为机器入口。不设主站读者名单，也不创建 Everyone Access 放行策略。旧 GitHub Pages 和原 Pages holding 保留；不改 DNS、不购买域名、不升级套餐，其他项目保持各自访问方式。

## 仓库构建配置

读取目标 Git revision 下的 `cloudflare-builds.yaml`、`package-lock.json` 与 `wrangler.jsonc`。根目录 `/`，主分支 `main`，静态输出 `_site`。

- Build：`npm ci --ignore-scripts --no-audit --no-fund && python tools/build_public_site.py`
- Deploy：`npm run cloudflare:deploy`
- 非主分支：`npm run cloudflare:preview`
- 目标工具版本：Python 3.12.12、Node 22.22.0、Wrangler 4.136.1。必须从实际构建日志复核，不能把配置当成运行证据。

holding 构建在 Python 命令后加 `--holding`。最初 Worker holding 是直接 API 引导部署，不是 Git 构建；当前主站已由 Starter 的 Git 构建提供完整候选内容，不能再把历史 holding 视作当前主站版本。

## 云端执行

1. 先读[仅依赖 GitHub 的交接说明](CLOUDFLARE_WEB_AGENT_HANDOFF.zh-CN.md)和[已完成验收](CLOUDFLARE_DEPLOYMENT_ACCEPTANCE.zh-CN.md)，再 fresh-read 实际提供商状态。复用 Worker、构建连接和账户前缀，不重复创建。
2. 当前原生 Workers Builds 已只连接 Starter，`main` 更新会触发完整站点构建。新增仓库的 GitHub App 授权仍由人批准；原生 user build token 不宣称单 Worker 最小权限，秘密不得进入 Git、聊天或日志。
3. GitHub App 已在四个选定仓库安装，按权限最小化的临时安装令牌通知 Starter，并由 App 创建来源锁 PR；普通 PR 检查通过后合并，随后原生 Builds 部署。没有定时轮询。具体权限与失败恢复见 [GitHub App 契约](GITHUB_APP_PUBLICATION.zh-CN.md)。
4. 预览 URL 与非主分支自动构建继续关闭。若以后批准预览读者，先配置 `preview_worker` Access 保护并审查优先级更高的 hostname 策略，再同时启用预览 URL 与非主分支构建，实际测试匿名拒绝与获准身份可读。预览上传不能替换主部署。
5. 本次正式切换后，以实际部署 revision、`/build-info.json`、`/agent/entry.json`、全部组件路径、双语及无 JavaScript 内容为准，核对 canonical 链接、`robots.txt` 与响应头不再带候选版 `noindex`。结果通过后才将状态写为 `verified-cutover`；若失败，恢复上一已验证 Worker 版本并使用仓库 revert。

## 回滚

每次部署前重新读取当前部署并保存非秘密版本引用。候选失败优先恢复私有状态中记录的上一已验证 Worker 版本，或通过正常 PR revert 来源锁，然后检查实际响应；必要时暂停自动触发器。旧 holding 是历史恢复点，使用前必须重新确认可用。若秘密发生变化，不得强制绕过回滚阻止而不检查影响。保留 Pages holding、GitHub Pages、已有域名及其他项目 App 授权，不强推或删除项目。

## 官方依据

核对日期 2026-09-22；操作前仍需复核 live API/UI：

- [Workers 建议](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/)
- [Workers Builds API](https://developers.cloudflare.com/workers/ci-cd/builds/api-reference/)
- [主站与预览 Access](https://developers.cloudflare.com/workers/configuration/cloudflare-access/)
- [workers.dev](https://developers.cloudflare.com/workers/configuration/routing/workers-dev/)
- [静态资源计费](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/)
