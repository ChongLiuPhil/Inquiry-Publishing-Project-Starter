# Cloudflare 单站公共交付迁移

**状态：仓库侧准备；provider actual state 未验证；未执行 public cutover。**

2026-09-22 用户批准以一个综合网站、一个 Pages 项目取代四个 Pages 项目的旧方案。四个 GitHub 仓库继续独立维护规范、版本、PR 与 CI。完整决定见 [UNIFIED_PUBLIC_SITE.zh-CN.md](UNIFIED_PUBLIC_SITE.zh-CN.md)；机器计划见 [cloudflare-public-delivery.yaml](../templates/cloudflare-public-delivery.yaml)。

## 一个网站，两种入口角色

同一个尚待选择的自定义域名：`/` 是以 AHICP 为内容基础的人类入口；`/agent/` 是 Starter 的机器入口。组件栏目位于 `/ahicp/`、`/ppf/`、`/vault-interface/`、`/starter/`；`/start/` 提供启动说明。路径是批准的目标布局，不是已经存在的正式 URL。

GitHub 仍是 canonical source。当前四个 GitHub Pages URL、Human Entry、Machine Entry 与 About Website 均保持不变。静态框架网站使用 Pages；下游 PPF 项目仍按实际运行需要选择 Pages、Workers 或其他 provider。

## 构建设置

只连接 `ChongLiuPhil/Inquiry-Publishing-Project-Starter`；三个其他公开上游按锁定 SHA、不带凭据读取，不需要为本次构建扩大 GitHub App 权限。

```text
Production branch: main
Root directory: .
Framework preset: none
Initial build command: python tools/build_public_site.py --holding
Full candidate build command: python tools/build_public_site.py
Build output directory: _site
PYTHON_VERSION: 3.12
NODE_VERSION: 22
```

旧的 `exit 0` + `docs` 不适用于单站组合。先部署空占位页；访问保护验证前不要部署完整候选内容。不要因 Dashboard 把 main 标记为 Production，就把它解释为生态 public cutover。

## 最小人工门与 Agent 恢复点

1. 打开 `https://dash.cloudflare.com/`，登录并直接完成 MFA，选择实际目标账户。不要把密码、MFA、token、Cookie、私钥或恢复码发到聊天。
2. 进入 **Workers & Pages**，先检查是否已有对应 Pages 项目；不要重复创建或删除旧项目。首次连接进入 **Create application → Pages → Connect to Git / Import an existing Git repository**。这是 Pages 流程，不是 Worker 的 Deploy command 流程；UI 不同必须先核验当前官方文档/界面。
3. 在 GitHub App 授权页选择 `ChongLiuPhil`；仅为本任务新增 Starter 仓库权限。已经给其他实际项目的授权不得擅自撤销。完成条件：Cloudflare 可以看到 Starter。人类完成账户授权后，有实际已认证工具的 Agent 应接回常规配置工作；本地浏览器登录不自动建立 Agent 控制面会话。
4. 按上述初始设置创建/配置**一个** Pages 项目，项目名称尚未决定，不自动假定可用名称。先关闭自动 production/preview 部署，避免配置 Access 时上传完整网站；只部署 holding page。可回传的非秘密结果是项目名称、实际 `pages.dev` 地址和部署状态，不需要 token。
5. 项目 **Settings → General → Enable access policy** 只解决 preview 默认策略。按官方 Known issues 中的 exact-hostname 流程保护 `项目名.pages.dev`，并保留/重新建立 `*.项目名.pages.dev` 保护；在 Zero Trust Applications 中核验两者都存在。读者身份直接在 Cloudflare 中批准，不创建 Everyone 允许规则。不能把 wildcard preview 策略当成主地址保护；`noindex` 也不是认证。
6. 用匿名/无痕会话验证主地址和一个真实预览地址不能读取正文；用获准身份验证可读；检查直接文件、JSON、bootstrap、静态资源和替代 hostname。没有预览部署时，preview 检查保持待完成，不标记 PASS。
7. Access 验证后，Agent 把构建命令改成完整候选命令，执行受限部署，核对 `/build-info.json` 的 Starter revision 和三库固定 revision，再验证所有栏目、双语切换、无 JavaScript fallback、指南加载与机器资源。只写回非秘密项目标识、URL、revision 和实际验证结果；Access ID、读者身份等私人控制面数据留在获授权的私人 provider state。
8. 之后才由人类选择自定义域名并授权必要 DNS/zone 动作。域名验证与最终 public cutover 是不同的门：不要自动移除 Access、修改正式 URL 或关闭 GitHub Pages。

## 最终公开切换（尚未授权）

构建器当前故意只有 holding/candidate 行为。候选中的 canonical/public 字段继续记录旧正式入口，相对候选路径放在独立字段。得到最终明确授权后，另做协调 PR：更新四库 ecosystem、About Website、README 公共入口、llms、machine descriptor、retrieval contract、跨站链接与旧 URL 映射；修改候选提示、索引策略及相应验证器。GitHub 源仓库地址不变。

四库无法形成真正的跨仓库原子 Git 事务。应记录切换清单与每库 revision，在兼容窗口内保留旧入口，逐项核验，避免把协调切换称为不可分割的原子操作。

## 验证与回滚

GitHub CI 构建和浏览器测试通过，只证明候选工件；不证明 Cloudflare 的部署、TLS、DNS 或 Access 已完成。

切换前：继续使用所有旧 GitHub Pages URL；候选失败可恢复 holding build 或上一份已验证部署，并暂停自动构建。仓库变更用 revert PR 回滚。切换后：按已记录的清单恢复旧入口、About 与 DNS。不要删除 Cloudflare 项目或强推历史。每次部署后重新核验 provider actual state，而不是从 proposal 推断实际状态。

## 官方操作依据

核对日期：2026-09-22。实际 UI 仍须在操作时复核。

- https://developers.cloudflare.com/pages/configuration/git-integration/
- https://developers.cloudflare.com/pages/configuration/preview-deployments/
- https://developers.cloudflare.com/pages/platform/known-issues/
- https://developers.cloudflare.com/pages/configuration/branch-build-controls/
- https://developers.cloudflare.com/pages/configuration/build-configuration/
