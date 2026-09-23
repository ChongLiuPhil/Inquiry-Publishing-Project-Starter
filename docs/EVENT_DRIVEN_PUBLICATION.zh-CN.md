# 提交事件驱动的综合站更新

## 授权与行为

2026-09-23 人类批准：取消每小时轮询，四个框架仓库的已收录成品发生更新后自动验证并部署；未来作品通过明确登记接入，不自动收录其他仓库。当前主站允许公开阅读，正式 URL、DNS、旧站和付费计划不变。

三个上游默认分支每次 push 都发送通知，不设置文件路径过滤。Starter 通过 `workflow_dispatch` 接收 `repository / branch / revision`，核验注册来源、公开状态、默认分支及提交祖先关系，然后核对所有来源当前 head。通知只作为提示，不能提供 URL 或构建命令。旧事件不会将网站恢复到旧 SHA。核对全部来源可弥补 GitHub concurrency 替换等待任务造成的跨仓库通知合并；无提交时无检查，人工 recovery 除外。

输出相同时不提交、不部署；输出变化时固定完整 SHA，在提交前运行测试、完整构建、链接及来源验证。写锁失败不强推，修复后手动重跑。失败保留线上最后成功版本。Starter 自身 main 的更新沿用 Cloudflare Git 集成。GitHub bot 提交不触发普通 GitHub push 工作流，因此必要验证在更新工作流内部完成；Cloudflare 是否收到 bot push 必须实测。

## Token 一次性设置（账户所有者）

1. 打开 https://github.com/settings/personal-access-tokens/new 。名称 `inquiry-starter-sync`；建议有效期 90 天，到期后轮换。
2. Resource owner 选 `ChongLiuPhil`；Only select repositories 仅选 `Inquiry-Publishing-Project-Starter`。
3. Repository permissions 只增加 **Actions: Read and write**；保留自动的 Metadata read。不增加 Contents write。Actions write 可以管理该仓库的其他 Actions，不是只授权单个通知入口。
4. 直接把生成的值保存到下列三个仓库的 Actions secret，名称均为 `STARTER_SYNC_TOKEN`。不要把值发给 Agent、写入 Git、PR 或日志：
   - https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol/settings/secrets/actions/new
   - https://github.com/ChongLiuPhil/Personal-Publishing-Framework/settings/secrets/actions/new
   - https://github.com/ChongLiuPhil/Vault-interface/settings/secrets/actions/new
5. 三个页面均显示该名称即完成录入；通知工作流成功仅代表 Starter 接收，不代表部署成功。Agent 随后核验通知、来源锁提交、Cloudflare 构建和线上版本。

该秘密仅进入无 checkout、无项目构建的通知步骤。内容构建不接收 Token。撤销 Token 或删除三个 secrets 可停止通知；可在 Starter Actions 页面手动运行来源刷新恢复漏掉的更新。授权失败或到期时必须报告失败，不能静默成功。

## 发布清单及完整成品

`site/publications.json` 是发布范围的权威清单；`site/sources.lock.json` 固定来源版本。现有四个组件使用 `static-files` 和已批准页面列表，不复制整个 docs 树。新增书籍或应用在清单 `publications` 中登记唯一键及 `repository / branch / visibility: public / source_directory / output_directory / build / mount`；在来源锁的 `publications` 下以同一键记录 repository 和完整 revision。通知模板复制为来源仓库的 workflow，并配置同一个通知 secret。登记不同默认分支时同步修改模板 push 分支。

支持 `static-directory` 与 `quarto`。完整输出目录内的章节、图片、脚本、样式和下载附件自动收录，增删文件无需修改清单。输出需要 index.html；禁止路径越界、符号链接、隐藏文件、路径冲突和超限文件。网页必须使用适用于挂载路径的相对 URL；站点验证检查所有 HTML 的本地链接。成品每文件上限 25 MiB、总计 200 MiB；达到限制报错，不自动购买存储。

示例位于 `templates/publication-examples/static` 和 `quarto`；它们没有加入实际网站。将示例作为独立仓库使用时，public 或 _book 是唯一输出目录。Quarto 版本固定为 1.10.18，运行环境必须安装该版本；缺失或不同版本拒绝构建。未来登记 Quarto 时同时为验证和 Cloudflare 构建环境准备固定运行时，不允许跳过渲染。本轮当前四库没有 Quarto 运行时依赖。build_local 可在临时副本运行示例，build_remote 按固定 SHA 获取公共来源。

Quarto 子进程不继承 Token、用户 HOME 或 Git 配置，构建输出不直接打印；这是凭据隔离措施，不是任意恶意代码的安全沙箱。只有经过批准的公共构建配置可登记；私人项目应使用自己的受限交付流程，不通过此公共来源抓取器读取。

## 验收、状态及回滚

分别记录离线测试、真实固定来源构建、GitHub CI 和真实提交至部署验收。真实验收必须包含各上游通知、来源锁 revision、Starter commit、Cloudflare build/version 和在线 build-info.json；无变化事件确认没有锁提交或部署。Token 录入前不能宣称自动链路已完成。

回滚使用 revert PR 或恢复已验证 Worker 版本。通知失败时修复 Token 后重跑；构建失败先修复来源，再重跑。无需恢复 cron。免费额度不足时停止，等待恢复或单独人类决定；不自动付费。
