# 项目自动配置契约

**状态：** Starter 新项目基础设施编排的权威契约  
**首选 Infrastructure Profile：** `agent-provisioned-external-ci`

本契约规定 Inquiry Publishing Stack 如何把一个新项目请求转化为已采用、private-by-default、可部署的项目，同时尽量减少重复的人类授权。

Starter 负责**组合与 Provisioning 意图**；它不复制 Provider 实现。可执行 GitHub / Cloudflare infrastructure adapter、reconciliation、deployment profile 与验证由 PPF 负责。

## 1. 目标

平台 bootstrap 完成后，普通新项目应走：

```text
人类项目请求
-> Starter 校验 platform standing authorization
-> private GitHub repository
-> 完整 AHICP + 完整 PPF + Vault Interface
-> PPF project infrastructure manifest
-> account-wide Access 前置检查
-> Cloudflare Worker
-> trusted secret broker
-> GitHub Actions restricted deployment
-> live verification
-> 非秘密状态持久写回
```

只要项目仍处于已批准的 GitHub / Cloudflare scope 内，不应仅因为“又创建一个项目”就重复要求 Provider 授权。

## 2. 不建立第二套基础设施控制平面

Starter 不实现 Cloudflare / GitHub Provisioning API。

可执行 Provider authority 位于 PPF：

- `providers/infrastructure/provisioning.py`
- `providers/infrastructure/coordinator.py`
- `schema/project.infrastructure.schema.json`
- `docs/AGENT_PROVISIONED_EXTERNAL_CI.md`

Starter 负责选择 PPF Profile、创建 project-level request、检查 platform authorization、应用 Stack 模板，并保持人类决定边界。

## 3. Platform Authorization

可复用的非秘密授权状态由以下结构表示：

- `schema/platform-authorization.schema.json`
- `templates/platform-authorization.yaml`

Platform authorization 只保存 reference 和 verified state，绝不能包含 API token、私钥、密码、恢复码、OTP 或 reader identity。

平台只有在以下全部 verified 后才是 `ready`：

### GitHub

- 目标 owner / organization scope 已批准；
- provisioning principal 已对该 scope 授权。

### Cloudflare

- provisioning principal 已授权；
- account-wide `all_workers` Access baseline 已 verified；
- Worker creation authority 已 verified；
- account-owned token creation authority 已 verified。

### Secret Broker

- trusted broker implementation 已存在并通过验证，可以把 project deployment credential 直接写入 GitHub Actions，而不把明文暴露给 Agent/model。

## 4. Standing Authorization

Platform authorization 可以预先批准低风险、private-by-default 的项目初始化：

```yaml
standing_authorizations:
  create_private_repositories: true
  create_restricted_workers: true
  restricted_web_deployment: true
  public_release: false
  reader_audience_expansion: false
  custom_domain_change: false
  paid_plan_change: false
```

这表示后续项目无需再次要求人类确认：

- 创建 private repository；
- 创建由 account-wide Access 保护的 Worker；
- 部署 restricted/authenticated Continuous Web；
- 验证该部署。

它**不**授权：

- publication 变成 public；
- source repository 公开/open-source；
- 新增或扩大 reader；
- 新 Custom Domain 或 DNS 改动；
- Provider permission scope 扩大；
- 启用 paid plan。

## 5. Project Request

新项目使用：

- `schema/project-provisioning-request.schema.json`
- `templates/project-provisioning-request.yaml`

默认 Request 声明：

- `full-research-publication`；
- private GitHub source；
- `agent-provisioned-external-ci`；
- restricted Web；
- Preview disabled；
- `shared-reader-access`；
- 无 Custom Domain；
- 无 public-release authorization。

Request 不包含 credential material。

## 6. 项目组合

默认 full profile：

```text
完整 AHICP
+ 完整 PPF
+ Vault Interface
+ project-owned content
```

写入项目文件前，Agent 仍必须 fresh-read 固定版本的 upstream ownership manifest。

PPF 的新项目首选 infrastructure profile 是 `agent-provisioned-external-ci`。Workers Builds Native 继续保留给明确选择它的项目，或已有使用该 Profile 的项目。

## 7. Restricted Deployment Standing Policy

如果 `standing_authorizations.restricted_web_deployment` 为 true，且 Request 使用 `restricted_deployment_source: platform-standing-authorization`，Starter 可以在不再次逐项目询问的情况下物化 downstream PPF restricted Continuous Web authorization。

该授权只覆盖声明的 restricted/authenticated 状态。

不得设置或暗示：

- `visibility: public`；
- public Access bypass；
- source repository public；
- Custom Domain authorization；
- reader-audience expansion；
- public canonical cutover。

Public release 仍需单独的持久化人类批准。

## 8. Provisioning 顺序

Agent 应按以下顺序：

1. 读取 Starter ecosystem 与 retrieval contract。
2. 读取本契约。
3. 校验 platform authorization record。
4. 校验 project provisioning request。
5. 解析完整 Starter Profile 与固定 upstream source。
6. 在 private repository 中创建/采用项目文件。
7. Fresh-read PPF Provisioning Profile 与 infrastructure schema。
8. 调用 PPF provisioner。
9. 若 PPF 返回 `SECRET_BROKER_REQUIRED`，只把该非秘密 Request 交给 trusted broker。
10. 回读 GitHub Secret metadata；绝不读取 Secret 值。
11. 只有 standing authorization 或 explicit project authorization 覆盖时，才物化 restricted deployment authorization。
12. 运行 CI / deployment。
13. 验证 repository privacy、account-wide Access、deployed revision、anonymous denial、assets 与 rollback。
14. 把非秘密 ID/status 与 verification evidence 写回 private project state。
15. 遇到 human-reserved gate 前停止相应动作。

## 9. Human-Reserved Gate

只有请求超出 standing platform/project authorization 时才回到人类，包括：

- GitHub provisioning scope 扩大；
- Cloudflare provisioning scope 扩大；
- 缺少 account-wide Access bootstrap；
- trusted Secret Broker 不可用而必须 direct secret input；
- reader-audience 新增/扩大；
- public publication；
- source repository public/open-source transition；
- Custom Domain / DNS authority；
- paid-plan change。

Human gate 是可续办 checkpoint。Agent 应继续其他互不依赖且已授权的工作；gate 完成后重新读取 Provider state 并继续。

## 10. Secret 边界

Secret 永远不得进入：

- Starter template；
- `project-stack.yaml`；
- provisioning request；
- platform authorization YAML；
- issue / PR body；
- log；
- chat / model context。

PPF Provisioner 只返回非秘密 `ppf/secret-broker-request/v1`。

Secret Broker 是受信 execution boundary，不是 LLM prompt。

## 11. 完成标准

只有以下全部满足，项目才可报告为 **restricted-deployment verified**：

- 目标 private GitHub repository 已存在；
- full-stack adoption state 已记录；
- 目标 Worker 已存在；
- account-wide Access baseline 仍 verified；
- project deployment credential metadata 已安装；
- 预期 Git revision 已部署；
- production 匿名访问被 challenge / deny；
- 若启用 Preview，匿名 Preview 也被 challenge / deny；
- direct asset 不能绕过 Access；
- Git/chat/log 中不存在 Secret 值；
- rollback 已记录；
- Provider state 已写回且不含 credential material。

在明确 human approval 前仍必须报告：

`public_release: NOT AUTHORIZED`

## 12. Evidence Boundary

契约、Schema、Planner、PPF Provisioner、Workflow 与 CI 只能证明 implementation readiness。

第一个 production-grade acceptance 必须使用全新 test project，真实记录：

```text
project request
-> private repo
-> stack adoption
-> Worker
-> secret broker
-> GitHub Actions deploy
-> restricted anonymous denial
-> revision verification
-> durable write-back
```

只有这些证据存在后，Starter 才能把此路径称为 verified automatic default。
