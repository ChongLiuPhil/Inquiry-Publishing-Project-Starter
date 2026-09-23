# 单站公共交付：决定与实现

## 已批准的架构决定（2026-09-22）

用户批准四个独立 GitHub 仓库组成一个综合网站，由一个活动 Cloudflare Worker 交付，随后另行批准 `inquirystack.philohub.workers.dev` 成为正式公共身份。人类入口位于 `/`，机器入口位于 `/agent/`。本轮不涉及 DNS 修改或付费升级。

这取代旧的“四个 Pages 项目”迁移拓扑，不合并四个组件的规范权威。AHICP 仍负责主要人类理解内容；Starter 仍负责机器调取、组合与升级。PPF 与 Vault Interface 保持各自权威。下游项目不继承这个网站的公开状态或部署平台选择。

## 内容与路径

`/` 直接由固定 AHICP revision 的完整人类介绍页派生，保留原有深度解释、双语切换和中文无 JavaScript fallback，并增加统一导航。`/ahicp/` 保留组件入口；`/ppf/`、`/vault-interface/` 和 `/starter/` 组合各自上游的完整公共主页。`/start/` 给出简短启动路径。`/agent/`、描述符、双语 bootstrap 和 `/llms.txt` 可单独调取，不依赖浏览器交互。

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

## 已批准的公共交付

用户已批准 `https://inquirystack.philohub.workers.dev/` 为正式人类入口、`/agent/` 为机器入口。机器描述符明确指向这些路径；GitHub Pages 保留为旧入口和回滚路径。

构建器要求版本化迁移计划中精确的 Worker 地址和切换授权。正式输出含 canonical 链接，不再带候选版 `noindex`；预览仍关闭，等待单独的 Access 验收。只有部署与路径实际检查通过后，才把线上切换记为已验证。

## 验证与恢复

`Unified public site` CI 执行离线回归、真实固定上游构建、链接/脚本/来源完整性验证，以及桌面、移动端、无 JavaScript 浏览器检查。它没有 Cloudflare 凭据，也没有部署步骤。CI PASS 不等于线上提供商验收通过。

主站匿名公开阅读和所选 Worker 的正式身份均已获批准。预览保持关闭，直到访问保护和读者批准完成。线上状态见 [迁移指南](CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.zh-CN.md)。

仓库回滚使用普通 revert PR；不强推。保留原 GitHub Pages URL，必要时恢复上一已验证 Worker 版本；不删除 Cloudflare 项目、不撤销其他项目正在使用的 GitHub App 权限。
