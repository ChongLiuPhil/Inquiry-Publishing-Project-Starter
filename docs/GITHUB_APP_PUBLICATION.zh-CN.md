# 账户安装的 GitHub App 发布通知

这是默认的提交通知机制，替代向各上游分发个人访问 Token。它仍需要认证：App 私钥与 Webhook Secret 集中保存在 Cloudflare Worker Secrets。按需生成的安装凭据有效期不超过一小时，不落盘、不记录日志。

## 范围与一次性配置

1. 在 https://github.com/settings/apps/new 创建 `Inquiry Publishing ChongLiuPhil`，仅允许当前账户安装。Homepage 填本 Starter 仓库；OAuth 回调、用户授权与 Device Flow 保持未设置或关闭。
2. 保留 Webhook Active 和 SSL verification。URL 填 `https://inquirystack.philohub.workers.dev/_events/github`。账户所有者通过密码管理器生成强随机秘密，直接填入 Secret，不进入聊天或 Git。
3. 仓库权限只选 **Contents Read-only**、**Actions Read and write** 及自动 Metadata Read-only；其他权限不启用。事件只订阅 **Push**。由所有者提交创建与安装，Selected repositories 仅选 Starter、AHICP、PPF、Vault-interface。App 最大权限对全部安装仓库生效，不能宣称只授权 Starter；运行时生成的凭据进一步限制为 Starter Actions 写，不请求 Contents 写。
4. 所有者在 App 设置生成私钥，直接在 Cloudflare **Workers & Pages → inquirystack → Settings → Variables and Secrets** 保存类型 Secret、名称 `GITHUB_APP_PRIVATE_KEY`，值为完整 PEM。相同 Webhook Secret 保存为 Secret `GITHUB_APP_WEBHOOK_SECRET`。App ID 保存为普通文本 `GITHUB_APP_ID`，Agent 可以填写此非秘密 ID。全部为 Worker 运行时配置，不是 Build variables 或上游 Actions secrets；秘密值不交给 Agent。
5. 全部保存后重投初始 ping；200 仅证明签名入口正常。停用或移除上游旧 PAT 通知工作流，使每次提交只有一条通知路径。不再创建个人 Token。

仍复用 `philohub.workers.dev` 下的一个活动 Worker `inquirystack`。只有 `/_events/*` 优先调用 Worker，普通静态页面保持 assets-first。此配置不修改 DNS、正式 URL、读者策略或套餐。缺少秘密拒绝处理通知；预览保持关闭，等待独立 Access 验收。

## 行为、验证与限制

先验证 HMAC-SHA256，再解析 push；仅登记的公开来源及配置的默认分支可发送通知。Starter 自身提交由原生 Workers Builds 处理，避免循环。Starter 再次独立核验仓库、分支、SHA，通知不能提供命令。重复或过时投递可能启动检查，但不能重复部署或回退版本，见[接收契约](EVENT_DRIVEN_PUBLICATION.zh-CN.md)。

正文超过 2 MiB 返回 413；签名错误 401，未登记或私库 403，分支漂移 409，配置缺失 503，GitHub API 错误 502。202 只表示已接收或按规则忽略，不表示部署完成。分别检查 Recent deliveries、Starter 刷新日志、锁提交、Cloudflare Build 和在线 build-info.json。GitHub 不自动重试失败的 Webhook：修复后在 App 设置重投，或手动运行 Starter refresh。不增加 cron。Webhook 包括被拒绝请求均消耗 Worker 请求额度；免费请求/CPU 与 Actions 额度不足时停止，不自动升级。

真实验收必须各测试一次上游成品变化和成品不变提交，核验签名投递、接收器比较结果、bot 锁提交、Cloudflare 原生构建及在线来源/版本。模拟测试与打包成功不能替代真实链路验收。

## 回滚

暂停 App 安装或关闭 Webhook 可停止通知，已部署静态网站继续可读。秘密泄露时双端轮换 Webhook Secret，或替换私钥并撤销旧密钥。通过 revert PR 恢复纯静态交付，或恢复已验证 Worker 版本；保留 Starter 人工刷新，不恢复每小时轮询。未来书籍和应用需要同时获得安装授权并登记发布清单；私人稿件不加入此公共来源流程。

## 受保护的来源锁发布

来源更新先验证成品，再用 Starter 的 GITHUB_TOKEN 推送确定的、仅修改来源锁的分支。GitHub 会把这次机器人推送签名后送至现有 Worker Webhook（已实测）。App 核验 Starter 身份、分支 SHA、单文件差异、公开范围不变、公开默认分支归属及来源版本只前进，然后以 App 身份创建 PR。临时安装令牌仅选择 Starter，权限仅为 Contents read 与 Pull requests write；令牌和私钥均不返回 Actions。重复通知复用已有 PR。

常规 PR CI 随后运行，无需 GITHUB_TOKEN 所创建 PR 的额外维护者批准。来源更新工作流等待固定提交的三项检查全部成功，再用 GITHUB_TOKEN 按正常分支规则合并。不会批准审查、修改必需检查或绕过保护；失败保留分支和 PR。App 尚未创建 PR 时可重放分支 Webhook，协调器中断时可运行来源更新的人工恢复入口。

所有者须在现有 GitHub App 中批准 **Pull requests: Read and write**，并接受安装权限更新。App 权限覆盖安装时选择的仓库；本实现把每次 PR 临时令牌进一步限制到 Starter。保留原有 Contents read、Actions write；无需新秘密、PAT、仓库或付费产品。上游通知仍只请求 Starter Actions write。仓库的 Actions 创建/批准 PR 开关不用于创建或批准这些 App PR。

GitHub 官方说明了 GITHUB_TOKEN 创建 PR 的工作流批准要求，并建议无人值守 PR CI 使用 App 安装令牌：https://docs.github.com/en/enterprise-cloud%40latest/actions/concepts/security/github_token 。合并后仍须独立核对 Cloudflare 原生构建和线上来源记录，不能把合并成功当作部署成功。
