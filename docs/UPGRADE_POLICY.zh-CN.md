# Stack 升级策略

升级不是“把模板重新复制一遍”。

标准流程：

1. fresh-read 当前项目、`project-stack.yaml` 与 lock；
2. 对每个 active component，读取其 `template_source_commit` 对应的上游 manifest；
3. ownership 分类直接以上游 manifest 为准，Starter 不复制 AHICP/PPF 的 ownership 列表；
4. upstream-managed 文件可依据目标 revision 更新；
5. merge-managed 文件做 base/current/new 三方比较；
6. project-owned 文件禁止自动覆盖；
7. deferred/not-applicable component 不进入安装或升级动作，对应 lock 必须为 null；
8. 严格区分模板来源 revision 与项目语义 adopted revision；
9. 先生成 branch / PR，运行项目自己的治理、出版与 runtime gates；
10. 合并后刷新 lock 与 portfolio/Vault summary。

旧项目已经有可靠文件时，优先 functional mapping，不为了形式一致制造第二套真值源。
