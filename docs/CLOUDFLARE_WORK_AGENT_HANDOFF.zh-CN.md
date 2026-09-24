# Cloudflare Work / Browser Agent 交接 Prompt

把下面内容作为 ChatGPT Work 或其他 browser-capable Agent 的任务 prompt：

> 打开目标 Cloudflare account，按照仓库契约配置项目的 private Continuous Web。修改 Provider state 前，先读取 Starter ecosystem、Agent Retrieval Contract、Project Provisioning Contract、Continuous Web / Cloudflare guide、Cloudflare 最小人类操作交接、项目 publishing.yaml / cloudflare-builds.yaml，以及固定版本 PPF 的每项目 setup guide。
>
> 普通新项目默认使用个人 ChongLiuPhil GitHub 账号、private repository、workers-builds-native、Worker-scoped Cloudflare Access，并保持 Preview disabled。除非项目显式选择高级 External-CI Profile，不得把账户级 Project Provisioner 基础设施当成前置条件。
>
> 改动前恢复并报告准确的 Cloudflare account、Worker/project、GitHub repository、production branch、build/deploy command、publication authorization state、预期 Access mode/policy 与当前 repository connection。
>
> 所有可以安全由浏览器完成的步骤都由你直接完成。默认 Profile 只有在确实需要账户所有者操作时才返回人类：GitHub / Cloudflare 登录或 MFA、当前 repository 的 Cloudflare Git authorization、reader identity policy 的选择/批准，以及 publication / domain / billing 等 human-reserved decision。绝不要要求人类把密码、API token、私钥、恢复码或其他 secret 粘贴到聊天。
>
> 把目标 private repository 连接到 Workers Builds，保持 non-production / preview build disabled，验证第一次 deployment；除非已有 verified account-wide protection，否则给 Worker 启用 Access 并选择 All traffic，然后验证匿名拒绝与已认证访问。
>
> 随后做或请求一次无害 source update，验证第二次 push 能自动 redeploy 且不需要重新 GitHub / Cloudflare authorization。第二次 push 没通过以前，不得把项目写成 operationally verified。
>
> 未经人类明确授权，不得把 restricted publication 改成 public、把 repository 改成 public、扩大 reader、改变 DNS / Custom Domain authority、扩大 Provider permission 或开启 paid plan。
>
> 最后输出不含秘密的 verification report，记录 actual Provider ID / URL、source revision、repository connection state、Access policy/application ID、第一次 deployment 与第二次 push 的 PASS/FAIL、rollback 信息，以及仍需人类决定的事项。
