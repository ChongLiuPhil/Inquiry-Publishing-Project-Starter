# 项目自动配置验收

**目的：** 对 `agent-provisioned-external-ci` 做真实端到端 live acceptance。

Repository CI、mock 与 Provider API 模拟均不能替代本验收。

## 前置条件

- platform authorization 已在私人状态中记录并校验为 ready；
- account-wide Cloudflare Access protection 已 verified；
- GitHub / Cloudflare provisioning principal 位于已批准 scope；
- trusted Secret Broker 可用；
- pilot slug 对应 repository / Worker 事先不存在；
- 不需要 Custom Domain、DNS 改动或付费产品。

## Pilot

使用可丢弃 project slug，且不得包含用户 manuscript 或本地电脑材料。

1. 用默认 full stack + External-CI Profile 新建 Provisioning Request。
2. 生成并审核 Starter Provisioning Plan。
3. Fresh-read 固定 AHICP / PPF / Vault manifest。
4. 由已授权 GitHub provisioning principal 创建 private repository。
5. 把固定 Stack / Template 组合进 repository。
6. 再次验证 account-wide Access 后才创建 Worker metadata。
7. Source deployment 前确认新 workers.dev endpoint 不可匿名读取。
8. 让 PPF Provisioner 输出 Secret Broker request。
9. Trusted broker 创建 individual-Worker Editor credential 并安装 GitHub Actions Secret；明文不得返回 Agent。
10. 运行 repository validation 与 deployment workflow。
11. 确认预期 Git SHA / revision 已部署。
12. 确认 production 匿名访问被 deny/challenge。
13. 如果 pilot 已明确批准 reader，则验证授权 reader 可读；否则不得自行发明 reader，只验匿名拒绝。
14. 匿名直接请求至少一个生成 asset，确认同样被 deny/challenge。
15. 确认 Preview URL 仍 disabled；Preview 作为后续独立验收。
16. 确认 repository history、Actions log、issue、PR、Agent output 与公共 metadata 中没有 Secret 值。
17. 在 private state 中记录非秘密 repository ID、Worker ID/name、deployed revision、Access reference、verification timestamp 与 rollback target。
18. 再触发一次后续 source change，确认同一 project-scoped credential 可以 deploy，且无需新的 platform authorization。
19. 无实质 source change 时再运行，确认没有意外 infrastructure drift。
20. 回滚到上一 verified deployment/version，再恢复当前版本，并确认两个状态都保持 restricted access。

## Pass Criteria

只有以下全部成立才通过：

- 没有 per-project platform reauthorization；
- GitHub source 一直 private；
- account-wide Access 一直 enabled；
- routine CI authority 只限制到目标 Worker；
- token 明文从未进入 model / Git / log；
- deployment 与 revision verification 成功；
- production 与 direct asset 匿名访问被 deny/challenge；
- rollback 成功；
- 未发生 paid-plan、domain、DNS 或 public-release 改动。

## Evidence Record

记录 project slug、immutable commit ID、非秘密 Worker identity、workflow run ID、deployed version/revision、HTTP result、Access reference、rollback version、准确日期，以及失败/恢复步骤。

不得记录 token 值、私钥、OTP、reader identity 或账户私有 Secret。

验收通过后，通过 reviewed PR 把 PPF 与 Starter 从 `live-new-project-acceptance-pending` 更新为带日期的 verified state。
