# Cloudflare 单站 Workers 交付迁移

状态：holding 已部署；完整运行站点及 Workers Builds 尚未验证；正式 URL 切换未获批准。v3 契约替代旧 Pages 专用步骤，包括旧文档要求当前主站受 Access 保护的条件。

## 已批准目标

四个仓库独立维护，组成一个网站，由 `inquirystack` Worker 提供服务，地址为 `https://inquirystack.philohub.workers.dev`。`/` 是人类入口，`/agent/` 是机器入口。GitHub 为权威源；只连接 Starter，其他三个公开上游按 `site/sources.lock.json` 固定 revision 无凭据读取。网站来源锁与下游采用锁分开维护。

用户于 2026-09-22 明确批准当前综合站主地址匿名公开阅读，不设主站读者名单，也不创建 Everyone Access 放行策略。这不等于批准修改 ecosystem 正式 URL、About Website、DNS 或停用 GitHub Pages。保留原 Pages holding；其他项目保持现有访问方式。免费优先，不自动购买或升级；免费提供商地址可以经验证和独立批准成为正式身份。

## 仓库构建配置

读取目标 Git revision 下的 `cloudflare-builds.yaml`、`package-lock.json` 与 `wrangler.jsonc`。根目录 `/`，主分支 `main`，静态输出 `_site`。

- Build：`npm ci --ignore-scripts --no-audit --no-fund && python tools/build_public_site.py`
- Deploy：`npm run cloudflare:deploy`
- 非主分支：`npm run cloudflare:preview`
- 目标工具版本：Python 3.12.12、Node 22.22.0、Wrangler 4.136.1。必须从实际构建日志复核，不能把配置当成运行证据。

holding 构建在 Python 命令后加 `--holding`。现有线上 holding 是直接 API 引导部署，不是 Git 构建，不能把它记为某个 Starter checkout。

## 云端执行

1. 先读[仅依赖 GitHub 的交接说明](CLOUDFLARE_WEB_AGENT_HANDOFF.zh-CN.md)，fresh-read 实际提供商状态。复用 Worker 和账户前缀，不改账户全局子域名，不重复创建项目。
2. 审查仓库 PR，检查通过后合并。待合并实现从 PR head 读取；源文件和 Actions 工件均在 GitHub，不需要原电脑文件。
3. 通过已有 Cloudflare GitHub App 只连接 Starter；新仓库授权仍由人批准。按上述配置使用原生 Workers Builds。未经核实不得借用其他项目的具名构建凭据；通过提供商 UI 或安全凭据流程选择/创建原生构建 token，秘密不得进入 Git、聊天或日志。原生 user-token 不宣称为单 Worker 最小权限。
4. 初始关闭非主分支自动构建和预览 URL。Access 团队初始化与预览读者仍未确定，不可为完成测试而公开预览。批准后配置 `preview_worker` Access 保护，并核查优先级更高的 hostname 策略；随后同时更新提供商与 Wrangler 配置，启用预览和非主分支构建。必须测试真实版本预览的匿名拒绝及获准身份可读。预览命令只上传版本，不替换主部署。
5. 运行完整主分支构建，记录真实 commit、deployment/version，匿名验证 `/`、`/agent/`、全部栏目、双语、移动端、无 JavaScript 内容、JSON、bootstrap、CSS 与 `/build-info.json`。核对四库来源 revision。保留现有正式 URL 与候选提示。
6. 实际验证一次 Git 提交触发构建，并确认第二次对账不新增重复连接、触发器或策略。手动触发成功不能代替 Git 事件衔接验证。
7. 分别记录提议、执行、本地/CI 测试和线上验证。通用 PPF 生命周期工具与共享密码模式的剩余实现见交接说明。

## 回滚

每次部署前重新读取当前部署并保存非秘密版本引用。已观察到的 holding 版本在交接记录中，使用前确认仍存在。候选失败恢复经验证的 holding 或上一版本，再检查实际响应；必要时暂停自动触发器。若秘密发生变化，不得强制绕过回滚阻止而不检查影响。仓库使用 revert PR；保留 Pages holding、GitHub Pages、已有域名及其他项目 App 授权，不强推或删除项目。

## 官方依据

核对日期 2026-09-22；操作前仍需复核 live API/UI：

- [Workers 建议](https://developers.cloudflare.com/workers/best-practices/workers-best-practices/)
- [Workers Builds API](https://developers.cloudflare.com/workers/ci-cd/builds/api-reference/)
- [主站与预览 Access](https://developers.cloudflare.com/workers/configuration/cloudflare-access/)
- [workers.dev](https://developers.cloudflare.com/workers/configuration/routing/workers-dev/)
- [静态资源计费](https://developers.cloudflare.com/workers/static-assets/billing-and-limitations/)
