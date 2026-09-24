# 项目 Provisioning 验收

**用途：** 对默认 `workers-builds-native`“每项目一次引导式 bootstrap”进行真实验收。

该验收是项目级的，不要求账户级零人工 Provisioning。

## 前置条件

- Project Request 校验通过；
- 目标 GitHub owner 为 `ChongLiuPhil`；
- repository 已是或将以 private 创建；
- 项目采用固定版本 PPF；
- Public release 未授权；
- Preview 默认关闭。

对默认 Profile，公共 `platform-authorization.yaml` Template 可以继续保持 `unconfigured`。

## 验收步骤

1. 在 `ChongLiuPhil` 下创建或确认 private repository。
2. 应用完整 Starter 组合与固定 upstream revisions。
3. 校验生成的 PPF `project.infrastructure.json`。
4. 确认 Profile 是 `workers-builds-native`。
5. 在 Cloudflare Workers & Pages 中 Import / Connect 目标 GitHub repository。
6. 如果 GitHub 提示，为该 repository 授权 Cloudflare Git integration。
7. 配置 production branch `main`、root `/`、固定 PPF build command 与 deploy command。
8. 保持 non-production / preview build disabled。
9. Save / Deploy，并只记录非秘密 Worker / repository connection identifiers。
10. 给 Worker 启用 Cloudflare Access，选择 **All traffic**；如果已经有 verified account-wide Access 覆盖它，则记录并复用。
11. 核验 GitHub repository 仍为 private。
12. 核验第一次 build / deployment 成功。
13. 核验 deployed revision 与预期 Git revision 一致。
14. 核验匿名 production 请求被 challenge / deny。
15. 核验已批准 reader 完成认证后可以访问 publication。
16. 核验 direct asset URL 不能绕过 Access。
17. 对 source 做一次无害改动并 push 到 `main`。
18. 核验 Workers Builds 自动启动并部署新 revision。
19. 确认第 18 步不需要重新授权 GitHub repository，也不需要重新连接 Cloudflare。
20. 核验第二次 deployment 后 Access 仍然生效。
21. 记录 rollback / restore point 与非秘密 Provider state。

## 通过标准

只有以下全部成立才通过：

- repository owner 为 `ChongLiuPhil`；
- repository visibility 为 private；
- Workers Builds 连接正确 repository；
- production branch 为 `main`；
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

不得通过让使用者把 Provider token 粘贴到聊天来解决这些问题。

## 可选高级验收

高级 `agent-provisioned-external-ci` Profile 继续保留自己的更严格验收要求，包括 Trusted Secret Broker 与 granular-token evidence。它们不是默认 Native 路线的前置条件。
