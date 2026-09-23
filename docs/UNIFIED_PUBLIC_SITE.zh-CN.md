# 单站公共交付：决定与实现

## 已批准的架构决定（2026-09-22）

用户明确同意：四个独立 GitHub 仓库组成一个综合网站，由一个活动 Cloudflare Worker 交付；允许免费提供商地址经明确批准成为正式身份，自定义域名可选。人类入口位于 `/`，机器入口位于 `/agent/`。批准范围包括可逆的仓库实现、PR、验证与状态写回；不包括域名选择、账户授权、DNS 修改或最终 public cutover。

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

来源更新由提交事件触发，不使用定时任务。三个上游默认分支提交后，通过账户安装的 GitHub App 签名事件通知 Starter；实际短期安装凭据仅限 Starter Actions 写权限。Starter 验证通知并核对所有公开来源的默认分支，比较成品，构建验证通过后提交固定来源 SHA。重复通知或成品未变化时不部署。每个事件都核对全部来源，避免 GitHub 替换排队任务后漏掉另一仓库的更新。见[配置及验收契约](EVENT_DRIVEN_PUBLICATION.zh-CN.md)。

发布范围由 `site/publications.json` 管理。框架页面保留已批准的明确文件；登记的书籍和应用发布完整输出目录，包括新章节、二进制资源和下载附件。首次登记或扩大公开范围经过审核；已批准成品目录内部的正常增删改无需逐个文件批准。免费额度不足时停止，不自动付费。

## 当前状态与候选状态

当前正式人类入口和机器入口在单独批准切换前仍为 GitHub Pages。候选描述符保留 `public_landing` 与 `human_entry`，另以 `delivery_candidate` 声明相对路径。只有经过验证并获正式切换批准后，Workers 地址才可成为正式身份。

候选输出带迁移提示和 `noindex`。**noindex 不等于访问认证。** 构建器目前故意仅支持 candidate/holding，不支持无授权 production 模式；最终切换必须通过单独的、明确授权的协调变更，更新公共 URL、候选提示、索引规则与相关验证器。

## 验证与恢复

`Unified public site` CI 执行离线回归、真实固定上游构建、链接/脚本/来源完整性验证，以及桌面、移动端、无 JavaScript 浏览器检查，并保存候选构建和截图。它没有 Cloudflare 凭据，也没有部署步骤。CI PASS 不等于 provider Access PASS。

Worker holding 已创建。用户随后明确批准主站公开阅读，无需 Access 名单；完整候选可在构建验证后部署。预览保持关闭，直到访问保护和读者批准完成。正式入口切换仍需独立批准。具体步骤见 [迁移指南](CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.zh-CN.md)。

仓库回滚使用普通 revert PR；不强推。切换前继续使用全部现有 GitHub Pages URL。候选部署可恢复占位页或之前验证过的部署；不删除 Cloudflare 项目、不撤销其他项目正在使用的 GitHub App 权限。
