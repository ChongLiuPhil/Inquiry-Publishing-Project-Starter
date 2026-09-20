# AI 采用与升级工作流

本文件给未来 AI Agent 一个统一、可执行的入口。

使用本工作流前，先阅读 docs/ECOSYSTEM.zh-CN.md、ecosystem.yaml 与 docs/AGENT_RETRIEVAL_CONTRACT.zh-CN.md。

## 新项目

1. 默认使用 full-research-publication：完整 AHICP + 完整 PPF + Vault Interface。精简 profile 必须由人类明确选择。
2. 对原创或未发布内容，canonical 源仓库默认建立或保持为 private。不要因为未来会公开 Web 就推断源仓库也应公开。
3. 读取 project-stack.yaml、目标 profile、stack/source-map.yaml 与 stack/managed-paths.yaml。
4. 把实际使用的 Starter source commit 写入 starter.adopted_commit；不得用下游项目自己的 HEAD 代替。
5. 运行 python tools/stack.py adoption-plan --json。
6. 对每个 active component，在 template_source_commit 上 fresh-read 它自己的 manifest；文件 ownership 以上游固定 revision 的 manifest 为唯一权威。
7. 对人类明确选择 deferred 的组件，不复制其模板、不虚构 adopted revision，并保持对应 lock 为 null。
8. 根据 profile 组合项目；可靠既有文件优先 functional mapping，不制造第二套真值源。
9. 保留人类已批准决定、publication authorization、canonical identity 与 provider actual state。
10. 涉及 Continuous Web 时，未发布或过渡阶段 Web 默认 restricted，reader access 使用 authenticated policy reference，例如 shared-reader-access；绝不把真实秘密写入 Git。
11. 在 access、preview、verification 与人类 publication gate 完成前，deployment 保持 staged，publication 保持 not-authorized。
12. 运行项目适用的 stack、治理、构建、出版与 runtime gates。
13. 通过 branch / PR 提交。
14. 只有所有 source revision 都明确后才运行 python tools/freeze_stack_lock.py，然后同步私人 portfolio summary。

## 已有项目升级

1. 读取当前 stack 与 lock，确定 active/deferred 状态。
2. 恢复四组件生态，并 fresh-read 当前项目与目标 template source revision 的上游 manifest。
3. ownership 分类直接以上游 manifest 为准；Starter 不维护复制后的总表。
4. upstream-managed 只在 pinned manifest 允许时更新。
5. merge-managed 执行 base/current/new 三方比较。
6. project-owned 禁止自动覆盖。
7. 严格区分 template_source_commit 与 project_adopted_commit；模板升级不能静默改写项目曾经批准的框架 revision。
8. source privacy、access policy、publication authorization 与 provider actual state 除非人类明确改变，否则必须保留。
9. Web 改为 public 时，不得顺带把 private 源仓库改成 public。
10. 创建 PR 并运行全部适用 gate；影响真实 provider 时加入 runtime verification。
11. 合并后刷新 lock 与 Vault portfolio health summary。

## Cloudflare 人类交接

当 Cloudflare 步骤需要人类执行时，遵循 docs/CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md。必须提供准确编号步骤、秘密边界、完成证据，以及 Agent 随后会验证的状态。不能仅因为涉及 Cloudflare 就把机器可执行的常规工作交还给人类。

## 推荐的人类指令

> 按照 Inquiry Publishing Project Stack 检查目标 GitHub repository。默认采用完整 AHICP + 完整 PPF + Vault Interface。原创或未发布源文件保持 private，同时准备 restricted + authenticated 的 Continuous Web；保留已有内容、已批准决定、publication authorization、access-policy reference 与 provider actual state，并生成经过验证的升级 PR。只有我明确选择时才使用精简 profile。任何必须由我执行的 Cloudflare 步骤，都请给出准确编号 UI 操作，告诉我哪些秘密不能发送到聊天，并定义你随后会验证的完成条件。
