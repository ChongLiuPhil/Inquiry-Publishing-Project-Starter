# Inquiry Publishing Project Starter

这是 AHICP、PPF 与 Vault Interface 的**组合、安装和升级层**，不是第四套规范。

## 它解决什么

现有三层各自保持权威：

- AHICP：人类主导、AI 辅助的探究与创作治理；
- PPF：source → build → publish → release → archive；
- Vault Interface：公开、中性的 `project.yaml` / `website.yaml` 接口。

Starter 只负责把兼容版本组合起来，并让已有项目可以被检查、迁移和升级。

## Profiles

- `research-only`
- `publishing-only`
- `research-book`
- `full-research-publication`

Profile 是组件组合，不是价值等级。

## 新项目

从本仓库生成新 repository 后，使用 `templates/` 中的基础 contract，再由 AI 根据 `project-stack.yaml` 中固定的 upstream commit 从 AHICP / PPF 拉取对应模板。不要把 Starter 变成第二份 AHICP 或 PPF 真值源。

## 已有项目

先运行：

```bash
python -m pip install -r requirements-validation.txt
python tools/stack.py doctor
```

升级必须遵守 `stack/managed-paths.yaml`：

- upstream-managed：允许按固定 upstream revision 更新；
- merge-managed：需要三方比较；
- project-owned：不得因 stack 升级自动覆盖。

## 人类边界

项目目的、实质性研究判断、publication authorization、最终发布批准与账号授权仍由人类决定。Token、密码、private key 或其他 secret 不进入 Git 或聊天。


## 版本角色

对成熟项目，Starter 明确区分“模板来源版本”和“项目已批准的规范采用版本”。模板工具可以升级，而项目的人类批准语义不会因此被静默改写。详见 `docs/UPGRADE_POLICY.zh-CN.md`。
