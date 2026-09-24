# Cloudflare 最小人类操作交接

**状态：** private/restricted Continuous Web 的权威操作交接  
**新项目默认 Infrastructure Profile：** `agent-provisioned-external-ci`  
**Policy Reference：** `shared-reader-access`

本指南通过区分**平台 bootstrap**与**项目 provisioning**，把重复人类操作压到最低。

完整编排规则见 [PROJECT_PROVISIONING_CONTRACT.zh-CN.md](PROJECT_PROVISIONING_CONTRACT.zh-CN.md)。真正可执行的 Provider implementation 仍由 PPF 负责。

## 1. Canonical Access 模型

未发布/restricted 项目：

```text
restricted Worker hostname
-> Cloudflare Access
-> account-wide all_workers baseline
-> project / audience policy
-> authenticated reader
```

项目文件可以记录 access-policy reference。Reader identity、账户私有 application/policy ID、credential、OTP 与 token 值仍属于 private provider state。

通用共享静态密码不是新的 canonical 模型。

## 2. 最少人类角色

首选新项目 Profile 不要求每个项目再做一次 Cloudflare ↔ GitHub 授权。

人类通常只在以下边界操作：

### Platform bootstrap — 一次性/低频

1. 登录 Cloudflare 并完成 MFA。
2. 授权范围受限的 Cloudflare provisioning principal。
3. 建立并验证覆盖 `all_workers` 的 account-wide Access baseline。
4. 建立 trusted Secret Broker / token-minting boundary。
5. 授权 GitHub provisioning principal 访问预定 GitHub owner/organization scope。

### 之后仍由人保留的决定

- public release；
- 新增/扩大 reader；
- 新 custom/canonical domain 或 DNS authority；
- 扩大 GitHub / Cloudflare permission scope；
- paid-plan / billing change；
- trusted broker 不可用时的 fallback direct secret input。

在已经批准的平台 scope 内再创建一个 private/restricted 项目，**本身不是新的 human gate**。

## 3. Cloudflare Provisioning Principal

Platform principal 只应拥有实现真正需要的 capability，但“创建 Worker”比日常 deployment 权限更广。

Cloudflare 当前 Workers role 区分：

- product-level **Admin**：可以创建 Worker；
- individual-Worker **Editor**：可以更新/部署既有 Worker，但不能删除。

因此：

```text
platform provisioner
  -> Workers product Admin 用于创建

project CI
  -> individual Worker Editor 用于日常部署
```

绝不能把 platform provisioning credential 交给 project CI。

## 4. 高权限 Token-Minting 边界

自动创建 account-owned API token 本身是高权限账户动作。

Cloudflare 当前 account-token 文档要求创建/更新 account-owned token 的主体拥有较高账户 authority。因此，这项能力只能存在于 trusted Secret Broker / provisioning boundary。

语言模型与 project CI 都不能获得 token-minting authority。

Broker 应创建：

```text
account-owned API token
scope: specified individual Worker
role: Editor
```

并直接把它写入目标 repository 的 GitHub Actions Secret。

## 5. Secret Broker Contract

PPF Provisioner 只返回非秘密 `ppf/secret-broker-request/v1`。

Trusted broker 原子执行：

1. 解析目标 Worker；
2. 创建 scoped account-owned Worker token；
3. 获取 repository Actions-secret public key / 安全写入接口；
4. 写入 `CLOUDFLARE_API_TOKEN`；
5. 写入 `CLOUDFLARE_ACCOUNT_ID`；
6. 丢弃 token 明文；
7. 只返回非秘密安装状态与 ID。

绝不把 token 粘贴进聊天、PR、issue、repository file 或 Agent 可见 log。

## 6. Account-Wide Access Bootstrap

自动创建任何 project Worker 以前，必须验证 destination 覆盖 `all_workers` 的 Access application 或等价 account-wide baseline。

该 baseline 应覆盖现有和未来 Worker。

Provisioner 无法验证时必须 fail closed。

以后 production 公开应表现为准确的 project exception；不得为了公开一个项目而关闭 account baseline。

## 7. Reader Authentication

`shared-reader-access` 等 reusable policy 可以使用 One-Time PIN 等已批准 identity mechanism 与明确 reader audience。

不得为了省事建立 Everyone / 所有 email 均允许的规则。

每个 restricted 项目至少验证：

- anonymous request 被 challenge/deny；
- 已实际批准 reader 时，approved reader 可以访问；
- unapproved reader 不可访问；
- direct asset/feed/generated-file URL 不能绕过 Access。

Reader identity 属于 private state，不进入公共 project repository。

## 8. Platform Bootstrap 后由 Agent 执行

Platform authorization 已记录为 ready 后，Agent 通常应：

1. 校验 `project-provisioning.yaml`；
2. 确认 GitHub owner 位于批准 scope；
3. 再次验证 account-wide Access；
4. 调用固定版本 PPF Provisioner；
5. 创建/复用 private repository 与 restricted Worker；
6. 把非秘密 Broker Request 交给 trusted broker；
7. 只验证 deployment-secret metadata，不读取 Secret 值；
8. 运行 repository validation 与已授权 GitHub Actions deployment；
9. 验证准确 deployed revision 与 restricted HTTP behavior；
10. 只持久记录非秘密状态与 rollback evidence。

没有人类独立 public-release authorization 时，必须停在公开切换之前。

## 9. Workers Builds Native 备选

`workers-builds-native` 继续支持明确选择 provider-native Git integration 或已有采用该 Profile 的项目。

该路径需要 Cloudflare Workers & Pages GitHub App 与 repository authorization；build credential 仍是 user-token 模型，而不是首选的 one-Worker account-owned deployment identity。

没有明确 migration plan 时，不得在同一项目混用两种 Profile。

## 10. 完成门

Restricted Continuous Web 只有在以下全部成立时才完成：

- private GitHub source identity 正确；
- account-wide Access 仍 verified；
- target Worker 正确；
- project deployment Secret 已安装且没有 Secret disclosure；
- repository/build gate 通过；
- deployed revision 与 intended source 一致；
- production anonymous access 被 challenge/deny；
- direct asset 不可绕过 Access；
- 已启用 Preview（如有）独立受保护；
- rollback 明确；
- 只把非秘密 Provider state 写回。

Deployment success 不构成 public-release authorization。
