# AI 采用与升级工作流

本文件给未来 AI Agent 一个统一、可执行的入口。

## 新项目

1. 读取 `project-stack.yaml`、目标 profile、`stack/source-map.yaml` 与 `stack/managed-paths.yaml`。
2. 把实际使用的 Starter source commit 写入 `starter.adopted_commit`；不得用下游项目自己的 HEAD 代替。
3. 运行 `python tools/stack.py adoption-plan --json`。
4. 对每个 **active** component，在 `template_source_commit` 上 fresh-read 它自己的 manifest；文件 ownership 以上游固定 revision 的 manifest 为唯一权威。
5. 对 deferred 的可选组件，不复制其模板、不虚构 adopted revision，并保持对应 lock 为 null。
6. 根据 profile 组合项目；可靠既有文件优先 functional mapping，不制造第二套真值源。
7. 保留人类已批准决定、publication authorization、canonical identity 与 provider actual state。
8. 运行项目适用的 stack、治理、构建、出版与 runtime gates。
9. 通过 branch / PR 提交。
10. 只有所有 source revision 都明确后才运行 `python tools/freeze_stack_lock.py`，然后同步私人 portfolio summary。

## 已有项目升级

1. 读取当前 stack 与 lock，先确定 active/deferred 状态。
2. fresh-read 当前项目以及目标 template source revision 的上游 manifest。
3. ownership 分类直接以上游 manifest 为准；Starter 不维护复制后的总表。
4. upstream-managed 只在 pinned manifest 允许时更新。
5. merge-managed 执行 base/current/new 三方比较。
6. project-owned 禁止自动覆盖。
7. 严格区分 `template_source_commit` 与 `project_adopted_commit`；模板升级不能静默改写项目曾经批准的框架 revision。
8. publication authorization 与 provider actual state 除非人类明确改变，否则必须保留。
9. 创建 PR 并运行全部适用 gate；影响真实 provider 时加入 runtime verification。
10. 合并后刷新 lock 与 Vault portfolio health summary。

## 推荐的人类指令

> 按照本仓库的 Inquiry Publishing Project Stack 检查目标 GitHub repository；选择与现有项目复杂度相符的 profile；保留已有内容、已批准决定、publication authorization 与 provider actual state；优先 functional mapping；生成并验证升级 PR。只有遇到身份授权、账号所有者确认、明确保留给我的 policy decision，或工具无法执行的 UI 操作时再交给我。
