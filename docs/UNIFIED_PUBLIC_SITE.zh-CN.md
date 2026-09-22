# 单站公共交付：决定与实现

## 已批准的架构决定（2026-09-22）

用户明确同意：四个独立 GitHub 仓库组成一个综合网站，由一个 Cloudflare Pages 项目交付；未来使用一个尚待选择的稳定自定义域名。人类入口位于 `/`，机器入口位于 `/agent/`。批准范围包括可逆的仓库实现、PR、验证与状态写回；不包括域名选择、账户授权、DNS 修改或最终 public cutover。

这取代旧的“四个 Pages 项目”迁移拓扑，不合并四个组件的规范权威。AHICP 仍负责主要人类理解内容；Starter 仍负责机器调取、组合与升级。PPF 与 Vault Interface 保持各自权威。下游项目不继承这个网站的公开状态或部署平台选择。

## 内容与路径

`/` 直接由固定 AHICP revision 的完整人类介绍页派生，保留原有深度解释、双语切换和中文无 JavaScript fallback，仅增加统一导航与迁移提示。`/ahicp/` 保留组件入口；`/ppf/`、`/vault-interface/` 和 `/starter/` 组合各自上游的完整公共主页。`/start/` 给出简短启动路径。`/agent/`、描述符、双语 bootstrap 和 `/llms.txt` 可单独调取，不依赖浏览器交互。

网站只是公共交付层，不是第四套规范或第二套可独立编辑的规范副本。未纳入公共输出白名单的文档只链接到上游 GitHub，不把整个 `docs/`、Working Memory、手稿或私人项目复制进网站。

## 可复现构建

```sh
python tools/build_public_site.py
```

输出：`_site/`。不改写旧的 `docs/` 首页，不执行部署，不修改 GitHub About 或 DNS。

`site/sources.lock.json` 固定三个远端公开上游的完整 commit SHA；Starter 使用实际 build checkout，构建时记录真实 SHA，避免仓库自引用锁。锁文件只控制网站组合，不替代 `project-stack.yaml`、`template_source_commit` 或 `project_adopted_commit`。

构建只允许明确的公开仓库与文件列表，通过不带凭据的 HTTPS 读取远端文件。`build-info.json` 记录四个来源 revision、输入与输出 SHA-256、锁文件摘要以及工作区是否有已跟踪改动。获取失败或验证失败时构建退出，不以旧缓存或浮动 `main` 偷换固定来源。

上游更新不会自动混入网站：维护者/Agent 应 fresh-read 对应 manifest，审阅来源差异，更新 lock，提交 PR 并通过完整测试，再部署已验证的组合。不存在本次批准之外的定时任务或跨仓库自动写权限。

## 当前状态与候选状态

当前正式 Human Entry、Machine Entry、四组件 URL 仍是 GitHub Pages。候选描述符保留当前 `public_landing` 与 `human_entry`，另以 `delivery_candidate` 声明相对路径；不能把相对候选路径或 `pages.dev` 写成正式身份。首页中的可复制启动指令继续使用当前正式机器入口。

候选输出带迁移提示和 `noindex`。**noindex 不等于访问认证。** 构建器目前故意仅支持 candidate/holding，不支持无授权 production 模式；最终切换必须通过单独的、明确授权的协调变更，更新公共 URL、候选提示、索引规则与相关验证器。

## 验证与恢复

`Unified public site` CI 执行离线回归、真实固定上游构建、链接/脚本/来源完整性验证，以及桌面、移动端、无 JavaScript 浏览器检查，并保存候选构建和截图。它没有 Cloudflare 凭据，也没有部署步骤。CI PASS 不等于 provider Access PASS。

Cloudflare 第一次部署使用 `python tools/build_public_site.py --holding`。主 `pages.dev` 与预览通配 hostname 均经过 Access 验证后，才切换为完整候选构建。具体步骤见 [迁移指南](CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.zh-CN.md)。

仓库回滚使用普通 revert PR；不强推。切换前继续使用全部现有 GitHub Pages URL。候选部署可恢复占位页或之前验证过的部署；不删除 Cloudflare 项目、不撤销其他项目正在使用的 GitHub App 权限。
