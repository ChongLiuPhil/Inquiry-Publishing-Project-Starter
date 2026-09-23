# 综合站 Workers 交付验收记录

记录日期：2026-09-23。此记录描述已验证的部署快照；后续提交应以线上 `/build-info.json` 和 Cloudflare 当前部署为准，不能把这里的 SHA 当作浮动最新版本。`https://inquirystack.philohub.workers.dev/` 已成为获批的正式 URL。

## 原 GitHub Pages 站点停用：2026-09-23

再次核对 Worker 站点 26 个可通过 HTTP 读取的产物哈希和七个主入口后，四个原框架 GitHub Pages 站点已停用。它们原先均从 `main/docs` 发布，未设置自定义域名；恢复所需的原配置已保存于私有部署状态。GitHub 随后对 AHICP、PPF、Vault Interface、Starter 均返回 `has_pages: false`，旧页面 URL 返回 HTTP 404。仓库及源文件未删除。四个仓库的主页字段继续指向各自的 Worker 栏目。上一已验证 Worker 版本是直接回滚点；恢复 Pages 必须另行明确重新配置。

AHICP [PR #43](https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol/pull/43) 修正双语公开指南中的失效链接。PPF [PR #38](https://github.com/ChongLiuPhil/Personal-Publishing-Framework/pull/38) 和 Vault Interface [PR #15](https://github.com/ChongLiuPhil/Vault-interface/pull/15) 修正公开状态；PPF 还将 Schema 标识从已停用的 Pages URL 改为经检查返回 HTTP 200 的 GitHub 原始文件地址。Starter 刷新首先暴露工作流缺少 Python 依赖，[PR #42](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/pull/42) 已修复。成功重跑后，来源锁 [PR #43](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/pull/43) 创建并合并，固定三个上游的新 revision。Starter `a9d10ef4c5ffd8f15be7bb07624cc17bbaf93a88` 的 Cloudflare 原生构建成功，新 Worker 版本承载 100% 流量。线上 `/build-info.json` 固定 AHICP `2b6bbdeb9ac6af0e09bb704c54314afb8d0ec4c3`、PPF `585a42e29b5230ba38e6ee1faecdb9f7f488275a`、Vault Interface `b896ce373fe6345e0b8ad978d6fec5ce0b24b981`。26 个可通过 HTTP 读取的产物哈希、七个主路径、canonical、robots 和 404 再次通过；双语指南及四个 llms 入口均不含已停用的 Pages 主机名。

## 正式 URL 切换验收：2026-09-23

用户批准免费 `workers.dev` 地址作为人类 `/` 和机器 `/agent/` 入口。AHICP [PR #42](https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol/pull/42)、PPF [PR #37](https://github.com/ChongLiuPhil/Personal-Publishing-Framework/pull/37)、Vault Interface [PR #14](https://github.com/ChongLiuPhil/Vault-interface/pull/14) 更新公共入口。Starter 来源锁 [PR #37](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/pull/37) 固定三个精确版本；切换 [PR #38](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/pull/38) 三项检查通过并合并。首次 Cloudflare 干净构建缺少 PyYAML 而失败，旧已验证部署继续服务。修复 [PR #39](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/pull/39) 将锁定的 Python 依赖安装写入仓库契约和提供商实际构建命令，三项检查通过并成功部署。

成功部署后的线上 `/build-info.json` 记录 Starter `ccf8e27cf578b6fa82d6af3c41c4f8cc1a51124f`、AHICP `6d314c5d81d296b2e8a6dff7d4feea6aaf63b9de`、PPF `52ceb00b45efc86f7d1f635beb2e0da7201ed588`、Vault Interface `c6f4991556aa280f712ec43a40df39b916da9ba4`；来源锁 SHA256 为 `aea40b131c7678a9f6db67b5b7b1ff930244d5d4c8ffe82ad9257795fd1bd8d3`。构建记录显示工作树干净、`state: canonical-workers-dev` 和获批公共 URL；新版 Worker 承载 100% 流量。26 个可通过 HTTP 读取的产物 SHA256 全部匹配构建记录；`_headers` 由提供商消费。线上 `/`、`/agent/`、`/start/`、四个组件路径、机器描述、canonical 标签、robots 放行、无 `noindex` 及 404 均通过；已审核切换 PR 的本地浏览器检查覆盖 24 种页面、视口和 JavaScript 组合。

上一已验证部署对应 Starter `cd0ce5e5bbcfc64e34c13770929677daff69272a`，精确回滚版本保存在私有部署状态；回滚前先重新读取活动部署。在当时的切换快照中，四个旧 GitHub Pages 入口返回 HTTP 200；当前 Cloudflare 账户未列出 Pages 项目，Pages holding 不能视为已验证回滚点。未修改 DNS 或付费套餐。预览 URL 与非主分支构建仍关闭，受限预览及 Access 读者验证尚未验收。

## 早期候选站证据

## 实际部署和来源

- Cloudflare Worker：`inquirystack`；账户子域名前缀：`philohub`。原生 Workers Builds 仅连接 Starter 的 `main`，根目录 `/`，输出 `_site`。构建命令、部署命令及工具版本见 `cloudflare-builds.yaml`。
- 2026-09-23 的真实上游事件：PPF PR [#36](https://github.com/ChongLiuPhil/Personal-Publishing-Framework/pull/36) 合并为 `89854ad29196f2f70e01e246d3839e3daa4ea159`；GitHub App 通知触发 Starter [刷新运行](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/actions/runs/35859708040)，App 创建来源锁 PR [#35](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/pull/35)，三项普通 PR 检查通过后按现有分支规则合并。
- Starter 部署源码 revision：`cc5093b048aadd776c141d86db021109dec09b0d`。同次线上 `/build-info.json` 记录 AHICP `032407eccbb70691058bdcb5a73d326aa73dae84`、PPF `89854ad29196f2f70e01e246d3839e3daa4ea159`、Vault Interface `599cf997d46ef5f0ca21c4f47b326bd46077c671`。来源锁 SHA256：`7fb2481b21ecbb2e6e71c1f6f0cd0d3005129a5ae050f34ef23520debef8db79`。
- Cloudflare 的该次原生构建与部署已成功；对应提供商 Build、Deployment 和 Worker Version 标识保存在私有部署状态中，不写入公共仓库。PR #35 保留了可公开核查的端到端证据与线上来源记录。

## 验证结果与边界

- 上游提交 → App 通知 → Starter 来源锁 PR → CI → 合并 → Cloudflare Git 构建 → 主站内容更新，实际通过；无需按小时轮询。
- 线上公开提供的 26 个输出文件与 `/build-info.json` 所列 SHA256 一致；`_headers` 由提供商消费，另核对了实际响应头。`/` 在浏览器显示；`/agent/` 匿名请求返回 HTTP 200。
- 相同上游通知重放产生[刷新运行](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/actions/runs/35860034407)，成品不变，没有新锁提交、PR 或部署。
- 在这一早期快照中，主站已公开，但正式 URL 尚未切换。预览 URL 和非主分支自动构建关闭；受限预览、Access 读者身份和匿名拒绝 **未验收**。DNS 未更改，GitHub Pages 未停用，也未执行 Pages holding 删除或付费升级；当时并未独立核实该 Pages 项目是否存在。

## 回滚

部署故障先重新读取当前 Worker 部署及来源版本。可按正常 PR/检查流程 revert 来源锁变更，或恢复私有部署状态中记录的上一已验证 Worker 版本，并复核主站响应。上一已验证候选版本对应 Starter `c10798832cdf7b47990d36a888bbe93b455f3691`；私有记录保留精确提供商版本 ID。不得通过删除项目、强推或修改正式公共 URL 回滚。当前 Cloudflare 账户未列出 Pages 项目；若怀疑在其他账户，须先核实后才能将其当作恢复点。
