# 综合站 Workers 候选站验收记录

记录日期：2026-09-23。此记录描述已验证的部署快照；后续提交应以线上 `/build-info.json` 和 Cloudflare 当前部署为准，不能把这里的 SHA 当作浮动最新版本。主站 `https://inquirystack.philohub.workers.dev/` 已获准匿名公开阅读，但尚未成为生态系统正式 URL。

## 实际部署和来源

- Cloudflare Worker：`inquirystack`；账户子域名前缀：`philohub`。原生 Workers Builds 仅连接 Starter 的 `main`，根目录 `/`，输出 `_site`。构建命令、部署命令及工具版本见 `cloudflare-builds.yaml`。
- 2026-09-23 的真实上游事件：PPF PR [#36](https://github.com/ChongLiuPhil/Personal-Publishing-Framework/pull/36) 合并为 `89854ad29196f2f70e01e246d3839e3daa4ea159`；GitHub App 通知触发 Starter [刷新运行](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/actions/runs/35859708040)，App 创建来源锁 PR [#35](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/pull/35)，三项普通 PR 检查通过后按现有分支规则合并。
- Starter 部署源码 revision：`cc5093b048aadd776c141d86db021109dec09b0d`。同次线上 `/build-info.json` 记录 AHICP `032407eccbb70691058bdcb5a73d326aa73dae84`、PPF `89854ad29196f2f70e01e246d3839e3daa4ea159`、Vault Interface `599cf997d46ef5f0ca21c4f47b326bd46077c671`。来源锁 SHA256：`7fb2481b21ecbb2e6e71c1f6f0cd0d3005129a5ae050f34ef23520debef8db79`。
- Cloudflare 的该次原生构建与部署已成功；对应提供商 Build、Deployment 和 Worker Version 标识保存在私有部署状态中，不写入公共仓库。PR #35 保留了可公开核查的端到端证据与线上来源记录。

## 验证结果与边界

- 上游提交 → App 通知 → Starter 来源锁 PR → CI → 合并 → Cloudflare Git 构建 → 主站内容更新，实际通过；无需按小时轮询。
- 线上公开提供的 26 个输出文件与 `/build-info.json` 所列 SHA256 一致；`_headers` 由提供商消费，另核对了实际响应头。`/` 在浏览器显示；`/agent/` 匿名请求返回 HTTP 200。
- 相同上游通知重放产生[刷新运行](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter/actions/runs/35860034407)，成品不变，没有新锁提交、PR 或部署。
- 当前主站公开；预览 URL 和非主分支自动构建仍关闭。受限预览、Access 读者身份和匿名拒绝 **未验收**，不能记为通过。正式 URL、DNS、GitHub Pages 和原 Pages holding 项目未切换或停用；没有付费升级。

## 回滚

部署故障先重新读取当前 Worker 部署及来源版本。可按正常 PR/检查流程 revert 来源锁变更，或恢复私有部署状态中记录的上一已验证 Worker 版本，并复核主站响应。上一已验证候选版本对应 Starter `c10798832cdf7b47990d36a888bbe93b455f3691`；私有记录保留精确提供商版本 ID。不得通过删除项目、强推或修改正式公共 URL 回滚。
