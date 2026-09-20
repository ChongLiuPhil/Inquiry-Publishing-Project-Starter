# Cloudflare Work / Browser Agent 交接 Prompt

把下面内容作为 ChatGPT Work 或其他 browser-capable Agent 的任务 prompt：

> 打开目标 Cloudflare account，按照仓库契约配置项目的 private Continuous Web。修改 provider state 前，先读取 Starter ecosystem、Agent Retrieval Contract、Continuous Web/Cloudflare guide、Cloudflare 最小人类操作交接、项目 publishing.yaml / cloudflare-builds.yaml，以及当前 PPF provider runbook。
>
> 在执行改动前，恢复并报告准确的 Cloudflare account、Worker/project、GitHub repository、production branch、build/deploy/preview command、hostname、publication authorization state 与预期 Access policy。
>
> 原创/未发布 source 默认 private。Web publication 使用 reusable policy reference shared-reader-access 保护。优先使用 Cloudflare Access identity authentication + 明确允许的 reader email + One-Time PIN；不要自行发明或要求用户提供静态密码。
>
> 所有可由浏览器或 API 完成的常规步骤都由你直接完成。只有遇到 Cloudflare 登录/MFA、第一次 GitHub App authorization、API-token secret 的创建/捕获、reader identity 批准、已有 legacy secret 的直接输入、或最终 public-release approval 时才交还人类。绝不要要求人类把 secret 粘贴到聊天。
>
> 每个人类保留动作完成后自动继续。配置并验证 Access、Workers Builds、preview deployment、hostname protection、direct assets/feeds 与 rollback。没有人类明确授权，不得把 restricted publication 改成 public。
>
> 最后输出不含秘密的 verification report，记录 actual provider ID、URL、source revision、Access policy/application ID、各验证项 PASS/FAIL，以及仍需人类决定的事项。
