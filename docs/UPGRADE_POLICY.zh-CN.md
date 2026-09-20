# Stack 升级策略

升级不是“把模板重新复制一遍”。

标准流程：

1. fresh-read 当前项目与 `project-stack.lock.yaml`；
2. 读取目标 AHICP / PPF / Vault Interface revision；
3. 对 upstream-managed 文件可直接更新；
4. 对 merge-managed 文件做 base/current/new 三方比较；
5. project-owned 文件禁止自动覆盖；
6. 先生成 branch / PR；
7. 运行项目自己的治理、出版与 runtime gates；
8. 合并后刷新 lock 与 portfolio/Vault summary。

旧项目已经有可靠文件时，优先 functional mapping，不为了形式一致制造第二套真值源。
