# Web AI Agent 接续：只依赖 GitHub 与提供商

本文件是执行交接，不能把未完成事项当成已实现。最后整理：2026-09-23。读取本文件所在 PR 的最新 head；合并后读取 main。接手不需要原电脑、聊天附件或任何本地目录。

## 1. 已有授权与最新决定

- 执行 GitHub → Cloudflare 标准化部署与当前综合站迁移；四库保持独立，一个活动 Worker。
- 当前 Worker 名称 `inquirystack`，账户已使用 `philohub` 前缀；目标地址 `https://inquirystack.philohub.workers.dev`。
- 用户随后明确批准“当前这个综合站的 Access 不设读者名单，直接公开”。此决定替代早期的主站 Access 候选流程。主地址公开阅读不再等待读者批准。
- 预览仍按原计划受限；保护未验证前保持关闭。不要把主站公开授权扩大到预览或其他项目。
- 未批准正式 URL 改写、旧站停用或 DNS 改动。保留 GitHub Pages 与原 Pages holding。免费优先，不升级套餐或购买域名。
- 常规配置、仓库变更、测试、上传及 PR 已获授权。只有登录/MFA、GitHub App 新授权、读者批准、未定域名、DNS/zone 授权、秘密直接输入和正式入口切换需要人处理。
- 秘密只在安全存储或提供商秘密字段中；不得要求粘贴到聊天。读者名单、账户控制面状态、凭据引用留在私人状态中；公共 GitHub 只保留非秘密方法、配置和允许公开的交付证据。

## 2. 读取顺序与版本

先读取机器入口 `https://chongliuphil.github.io/Inquiry-Publishing-Project-Starter/agent/`，再 fresh-read 当前执行 revision 下：

1. `AGENTS.md`、`ecosystem.yaml`、`docs/AGENT_RETRIEVAL_CONTRACT.zh-CN.md`。
2. `docs/CLOUDFLARE_PUBLIC_DELIVERY_MIGRATION.zh-CN.md`、`templates/cloudflare-public-delivery.yaml`（v3）、`cloudflare-builds.yaml`、`wrangler.jsonc`、`package-lock.json`。
3. `site/sources.lock.json`、`project-stack.yaml`、`project-stack.lock.yaml`、`stack/source-map.yaml`；区分网站来源锁和采用锁，勿批量升级下游。
4. PPF 当前 main、`AGENTS.md`、`docs/CONTINUOUS_WEB_CLOUDFLARE.md`、安全 profile、Access profile、GitHub 授权 runbook、模板 manifest；按选定 revision fresh-read manifest。

准备分支基线：Starter `117e9981c4d712110800f5d94bb875164fb41689`；PPF `5fca3e99df588c338eca45915478a07a9cadc099`。这些不是最终 PR head，必须通过 GitHub 查询当前 SHA。

网站锁保持：AHICP `032407eccbb70691058bdcb5a73d326aa73dae84`；PPF `5fca3e99df588c338eca45915478a07a9cadc099`；Vault `599cf997d46ef5f0ca21c4f47b326bd46077c671`；Starter 使用实际 build checkout。不得把历史 holding 版本伪称为 Git 构建版本。

## 3. 已完成与证据边界

- Starter PR #23 当前 head `4afaae6eac41a118c95e99e6bf1efa35578e8474`；GitHub Actions run `35782060578`（Ecosystem validation）、`35782060584`（Stack CI）、`35782060575`（Unified public site）均 SUCCESS。PR 仍 OPEN，合并前需重新核对 main 未前进及当前 checks。
- 本地固定 SHA 完整构建及输出/来源验证通过；浏览器测试 24 项通过（8 路由 × 桌面、移动、禁 JS），包含双语切换和指南加载。Wrangler 4.136.1 dry-run 对实际完整 `_site` 成功。
- 本地测试运行环境 Python 3.9；CI 和 Workers Build 目标为 Python 3.12.12，真实 Worker 构建仍需核验日志。

- Starter 已有组合构建器、公开文件白名单、来源记录、双语页面、无 JS fallback 和浏览器测试；本 PR 增加 Workers 配置、依赖锁、v3 契约与本交接。
- GitHub Actions `Unified public site` 是构建与验证流程，不部署，不需要 Cloudflare 凭据；从本 PR 对应运行读取真实结果和工件。
- 2026-09-22 09:56 UTC 实际创建 Worker holding，匿名主地址收到预期 HTTP 503、`Setup pending`、`Cache-Control: no-store`、`X-Robots-Tag: noindex`。这是主动返回的准备中页面，不是 Access 拒绝或完整站点验收。
- holding deployment：`a91fbe67-1bd1-4130-bbf4-31bc3dd9f817`；version：`88bb1d9a-acf7-4e52-8cd6-d9dfef3e9f3c`；当时 `workers.dev=true`、`previews_enabled=false`。先重新查询，不能假定状态未变。
- 原 Pages 项目 `inquiry-publishing-stack` 保留，曾成功部署 holding；不能把 Pages 成功推断为 Workers Builds 成功。
- 只有 Starter 的 Pages Git clone 曾验证成功，未核实 GitHub App 全部授权范围，不宣称最小权限。
- Access 当时返回未启用；Workers Builds API 可读且当时未耗尽构建分钟。用户账户前缀后已变为 `philohub`，本 Agent 没有执行账户改名。
- PPF PR #31（https://github.com/ChongLiuPhil/Personal-Publishing-Framework/pull/31）head `7b26191819645208a84a4bbc55d88f9087e1c032`；Reference Template CI run `35787073209` 与 Ecosystem validation run `35787073534` 均 SUCCESS，PR 仍 OPEN。该 PR 已提交生命周期 CLI、共享密码 Worker gate、项目模板、文档和测试，但尚未合并。当前仍无完整 Workers 内容部署、原生 Builds Git 触发验证或受保护预览验收。当前 `inquirystack` holding deployment/version 及 Builds 零 triggers 已于 2026-09-23 重新通过 Cloudflare API 核实。

## 4. 云端接续步骤

1. 在 GitHub 找到本文件所在 PR，核对 head、CI 和变更，完成必要修复后合并；版本和测试全部从 GitHub 读取。不要要求用户重新上传本地文件。
2. 优先使用现有授权的 Cloudflare API/MCP。浏览器备用路径须先实际读取并操作已有登录会话，不能另开不共享状态的远程浏览器后让用户重复登录。原桌面工具曾无法读取浏览器；这不证明你的环境也失败。
3. fresh-read Worker、账户子域名、部署、GitHub App、Builds 连接/触发器、额度和预览状态；不重复创建。
4. 在现有 `inquirystack` 的 Builds 中连接 Starter，根 `/`、主分支 `main`，其余使用 `cloudflare-builds.yaml`。只需要 Starter 仓库权限，其他三个上游无凭据固定 SHA 获取。
5. 原生 Builds 需要提供商管理的 user build token。现有其他项目的 token 名称不能证明可复用；核实范围/用途，必要时通过提供商正常创建流程准备凭据。秘密输入由人直接完成，不进入聊天或 Git。不要把原生 token 宣称为单 Worker 最小权限。
6. 执行完整主分支构建和公开部署；保留旧 canonical 字段、候选提示及 noindex，直到正式入口切换另获授权。
7. 验证 Git 提交真正触发构建，并核对实际 Python/Node/Wrangler、checkout SHA、三库来源 SHA、`/build-info.json`。匿名逐项验证 `/`、`/start/`、`/ahicp/`、`/ppf/`、`/vault-interface/`、`/starter/`、`/agent/`、descriptor、bootstrap、llms、CSS、双语、无 JS 和移动端。检查不存在页面不会错误返回首页。
8. 主站公开无需 Access 初始化。要完成受限预览时，才处理 Access 团队名称和预览读者批准；配置 `preview_worker` 并审查更高优先级 hostname 例外，验证真实版本预览。未完成就继续关闭，不伪报 PASS。预览上传不得替换主部署。
9. 保存非秘密部署、版本、验证与回滚证据到 GitHub 的执行报告；敏感控制面状态在私人提供商状态中保存。PR、CI 和 provider 各自证据独立记录。

## 5. 已提交与仍待完成的标准化工作

PPF PR #31 已提交生命周期 CLI `doctor / plan / apply / verify / rollback`、从项目模板读取部署配置、Workers Builds 与三种阅读模式的契约、共享密码服务端 gate、运行记录/受验证版本回滚机制及自动化测试。Starter 继续承担入口、锁和薄编排。以上属于开放 PR 中的代码，尚未合并；其中 `apply` 使用配置好的 Wrangler 命令，并不自动创建或协调 Workers Builds GitHub 连接/触发器。
- 从现有项目配置推导 repo、branch、build、output 和版本；综合站 `_site`，Quarto `_book`，保留原构建检查。
- 真实查询后按差异执行，幂等不重复创建 Worker/连接/trigger/policy；中途失败可从已验证步骤恢复；权限、额度、构建失败和漂移准确报错，不能自动放宽访问或付费。
- 优先已授权 API/MCP；独立脚本只用安全环境凭据，禁止输出秘密。提供原生 Workers Builds 默认 profile，保留强化 external CI profile。
- 三种阅读模式：获准 public、Access 邮箱名单（默认 OTP/24h）、可选项目共享密码。保留已有项目模式，新项目默认受限邮箱，未批读者停 holding；共享认证服务不等于共享读者名单。
- 密码模式用可复用 Worker 服务端模块，密码与签名密钥只入 Cloudflare Secrets；`run_worker_first` 覆盖 HTML/附件/JSON/资源/预览；恒时比较、签名有效期安全 Cookie、退出、尝试限速；任一秘密轮换使旧会话失效；禁公共缓存，秘密缺失/配置错误/认证异常/额度不足均 fail closed，不回退静态直出。明确边缘限速作用范围及 Worker 请求额度。
- 补齐双语操作契约、最小项目示例、模式验证器与测试；覆盖错误身份/密码、过期会话、轮换、直接附件、备用地址、缓存绕过、权限/额度/构建失败和恢复。测试通过不能替代真实 Access 身份和线上部署验证。
- 当前 PPF PR #31 尚未合并；Starter PR #23 未固定引用该 PPF revision。合并顺序及锁定采用需后续按 PR/基线核验。Workers Builds API 连接/触发器的自动幂等协调仍未实现，实际 GitHub App 授权必须由用户在 Cloudflare 页面完成；原生 user build token 及其安全录入亦未配置。

## 6. 完成与回滚

当前公开阅读已获用户授权，但生产 Worker 仍在 holding，尚未完成公开站内容部署/验收；最终正式 URL 切换仍需单独批准。预览保持关闭，直到 Access 保护及获批读者验证完成。

失败时暂停相关自动触发，恢复已验证 holding 或上一版本，复核响应；不删除项目、不强推、不改变其他项目。已知 holding 版本须先查询确认仍可用。仓库回滚使用 revert PR；不要自动恢复会泄漏内容的旧访问配置。
