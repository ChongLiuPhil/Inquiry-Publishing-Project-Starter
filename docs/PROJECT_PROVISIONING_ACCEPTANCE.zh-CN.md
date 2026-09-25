# 项目 Provisioning 验收

**用途：** 对默认 `workers-builds-native`“每项目一次引导式 bootstrap”进行真实验收。

该验收是项目级的，不要求账户级零人工 Provisioning。

## 前置条件

- Project Request 校验通过；
- 目标 GitHub owner 为 `ChongLiuPhil`；
- repository 已是或将以 private 创建；
- 项目采用固定版本 PPF；
- Project Request 声明 `ci_cost_profile: private-project-quota-saver`；
- Public release 未授权；
- Preview 默认关闭。

对默认 Profile，公共 `platform-authorization.yaml` Template 可以继续保持 `unconfigured`。

## 验收步骤

1. 在 `ChongLiuPhil` 下创建或确认 private repository。
2. 应用完整 Starter 组合与固定 upstream revisions。
3. 校验生成的 PPF `project.infrastructure.json`。
4. 确认 infrastructure profile 是 `workers-builds-native`，CI cost profile 是 `private-project-quota-saver`。
5. 确认 content-only 改动不匹配任何自动 GitHub Actions workflow；只有目标分支为 `main` 的配置 PR 匹配轻量 project contract check。
6. 在 Cloudflare Workers & Pages 中 Import / Connect 目标 GitHub repository。
7. 如果 GitHub 提示，为该 repository 授权 Cloudflare Git integration。
8. 把 Cloudflare Worker / application name 配置为与 `wrangler.jsonc.name` 完全一致，然后配置 production branch `main`、root `/`、固定 PPF build command 与 deploy command。
9. 保持 non-production / preview build disabled。
10. Save / Deploy，并只记录非秘密 Worker / repository connection identifiers。
11. 如果该 Cloudflare account 尚未启用 Zero Trust，先完成一次 Zero Trust setup；之后项目直接复用。
12. 给 Worker 启用 Cloudflare Access，选择 **All traffic**；如果已经有 verified account-wide Access 覆盖它，则记录并复用。已有批准的 authentication policy 时优先复用。
13. 核验 GitHub repository 仍为 private。
14. 核验 Cloudflare Worker / application name 与 `wrangler.jsonc.name` 一致。
15. 核验第一次 build / deployment 成功。
16. 核验 deployed revision 与预期 Git revision 一致。
17. 核验匿名 production 请求被 challenge / deny。
18. 核验已批准 reader 完成认证后可以访问 publication。
19. 核验 direct asset URL 不能绕过 Access。
20. 对 source 做一次无害的 **content-only** 改动并 push 到 `main`。
21. 核验 Workers Builds 自动启动并部署新 revision。
22. 核验第 21 步**没有**启动自动 GitHub Actions production Web build。
23. 确认第 21 步不需要重新连接 Git account、重新授权 Cloudflare GitHub App，也不需要重新连接同一 repository。
24. 核验第二次 deployment 后 Access 仍然生效。
25. 记录 rollback / restore point 与非秘密 Provider state。

## 通过标准

只有以下全部成立才通过：

- repository owner 为 `ChongLiuPhil`；
- repository visibility 为 private；
- Workers Builds 连接正确 repository；
- Cloudflare Worker / application name 与 `wrangler.jsonc.name` 一致；
- production branch 为 `main`；
- `ci_cost_profile` 为 `private-project-quota-saver`；
- content-only 改动不触发自动 GitHub Actions；
- 只有目标分支为 `main` 的配置 PR 使用轻量 contract gate；
- main push 不在 GitHub Actions 重复 production Web build；
- heavy GitHub workflow 为手动；
- 自动成功 run 不上传 artifact，手动 publication artifact 默认只保留 1 天；
- 使用 Worker-level Access 时 Zero Trust 已启用；
- 第一次 restricted deployment 已验证；
- Worker-scoped Access 或显式记录的 verified account-wide Access 已生效；
- 匿名访问被拒绝 / challenge；
- direct asset 继续受保护；
- 第二次 push 自动部署新 revision；
- 第二次 push 无需重新 Provider authorization；
- Git / chat / log 中不存在 credential value；
- 已记录 rollback / restore 证据；
- `public_release: NOT AUTHORIZED`。

## 失败处理

如果 Cloudflare 看不到 repository，只要求人类调整 Cloudflare GitHub App 对该 repository 的 access，然后重新读取 Provider state。

如果 Worker 可以匿名访问，停止声称 private readiness，并要求人类启用/修复 Cloudflare Access。

如果第二次 push 不能自动部署，即使第一次 deployment 成功，Project Bootstrap 仍未完成。

如果 content-only 改动启动了 GitHub Actions，或 main push 启动了重复的 GitHub production Web build，应视为 CI cost policy drift，修正 workflow trigger 后才能通过验收。

Private Actions allowance 已耗尽时，可选/手动 heavy check 可以保持 deferred；不得继续制造 blocked run，也不得在没有人类明确授权时开启付费 Actions 或修改 billing。

不得通过让使用者把 Provider token 粘贴到聊天来解决这些问题。

## 可选高级验收

高级 `agent-provisioned-external-ci` Profile 继续保留自己的更严格验收要求，包括 Trusted Secret Broker 与 granular-token evidence。它们不是默认 Native 路线的前置条件。
