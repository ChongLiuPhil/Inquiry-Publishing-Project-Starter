# Inquiry Publishing Stack：体系与 Agent 入口

本仓库是四个逻辑独立组件的组合入口：

| 组件 | 责任 | 公共入口 |
| --- | --- | --- |
| AHICP | 人类主导、AI 辅助的探究与创作治理 | [主页](https://chongliuphil.github.io/AI-Assisted-Human-Inquiry-and-Creation-Protocol/) · [仓库](https://github.com/ChongLiuPhil/AI-Assisted-Human-Inquiry-and-Creation-Protocol) |
| PPF | 以源文件为中心的出版、发布、归档和 Continuous Web | [主页](https://chongliuphil.github.io/Personal-Publishing-Framework/) · [仓库](https://github.com/ChongLiuPhil/Personal-Publishing-Framework) |
| Vault Interface | 与提供商无关的公共元数据 Schema 和验证器 | [仓库](https://github.com/ChongLiuPhil/Vault-interface) |
| Starter | 组合、采用、profile 和升级 | [主页](https://chongliuphil.github.io/Inquiry-Publishing-Project-Starter/) · [仓库](https://github.com/ChongLiuPhil/Inquiry-Publishing-Project-Starter) |

## 默认配置基线

每个新配置项目都应能够采用完整的 AHICP 治理层和完整的 PPF 发布层。项目通过 `project-stack.yaml` 记录实际采用状态，不复制出与上游规范竞争的第二套权威来源。

完整 profile 通常是：

```text
AHICP（完整）+ PPF（完整）+ Vault Interface（公共元数据）+ 项目自身内容
```

Vault Interface 是适配层，不替代 AHICP 或 PPF。只有在 profile 和 lock 文件明确记录时，项目才可以暂缓某个组件。

## 隐私与发布边界

- 未发布手稿、原创研究、个人工作记忆、凭据以及其他具有版权属性的源资产，默认属于私人内容。
- 公共仓库只包含可复用的方法、Schema、模板、验证器和说明，不包含私人项目状态。
- 私人项目仍然可以拥有 Continuous Web；但必须通过访问控制保护，不能把密码或密钥放进仓库或客户端源码。
- 私人控制平面只通过获得授权的项目配置被引用，不复制进公共 Starter。

## Agent 调取契约

AI agent 从任意组件主页或仓库进入时，应当：

1. 读取本文件和 `ecosystem.yaml`；
2. 确认当前组件，然后读取 AHICP 与 PPF 的上游入口；
3. 读取选定的 Starter profile 和 lock 文件；
4. 在固定版本处重新读取每个 active 上游 manifest；
5. 只有得到人类明确授权后，才检查私人项目状态；
6. 保持 proposal、authorization、execution、verification 和 durable write-back 的区分。

沿着公共链接进行调取是一套阅读协议，不等于获得私人仓库或私人部署系统的访问权限。

## Continuous Web 与 Cloudflare

详细操作指南见 [`CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md`](CONTINUOUS_WEB_CLOUDFLARE.zh-CN.md)，英文镜像见 [`CONTINUOUS_WEB_CLOUDFLARE.md`](CONTINUOUS_WEB_CLOUDFLARE.md)。

AI agent 在要求人类执行任何不可委托的 Cloudflare 操作前，必须说明所选架构、部署凭据范围、读者访问策略、密钥处理、验证门和回滚路径。
