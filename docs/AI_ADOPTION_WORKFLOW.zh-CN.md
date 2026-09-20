# AI 采用与升级工作流

本文件给未来 AI Agent 一个统一、可执行的入口。

## 新项目

1. 读取 `project-stack.yaml`、目标 `profiles/*.yaml`、`stack/source-map.yaml` 与 `stack/managed-paths.yaml`。
2. 运行 `python tools/stack.py adoption-plan --json`。
3. 对 adoption plan 中每个 component，使用声明的 repository + revision fresh-read 对应 manifest/template root。
4. 根据 profile 组合项目；替换占位符，但不要把上游 README/规范本体复制成项目真值源。
5. 运行项目本地 `stack-check` 与原有治理/构建 gate。
6. 通过 branch / PR 提交。
7. 采用完成后运行 `python tools/freeze_stack_lock.py` 固化 revision。
8. 如果项目由私人 portfolio 管理，再同步其 registry summary；注册不等于发布。

## 已有项目升级

1. 先读取当前 `project-stack.lock.yaml`，确认旧 upstream revision。
2. fresh-read 项目当前文件与目标 upstream manifests。
3. 对 `upstream-managed` 文件可按新 revision 更新。
4. 对 `merge-managed` 文件执行 base/current/new 三方比较。
5. 对 `project-owned` 文件禁止自动覆盖。
6. 已有可靠文件优先 functional mapping；不要仅为文件名一致性制造第二套真值源。
7. publication authorization、canonical identity、provider actual state 与人类已批准决定必须保留，除非人类明确改变。
8. 创建 PR 并运行全部项目 gate；需要真实 Web provider 时再做 runtime verification。
9. 合并后刷新 lock 与 Vault portfolio summary。

## 推荐的人类指令

> 按照本仓库的 Inquiry Publishing Project Stack 检查目标 GitHub repository；选择与现有项目复杂度相符的 profile；保留已有内容、已批准决定、publication authorization 与 provider actual state；优先 functional mapping；生成并验证升级 PR。只有遇到身份授权、账号所有者确认或工具无法执行的 UI 操作时再交给我。
