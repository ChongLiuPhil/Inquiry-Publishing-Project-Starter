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


## 机器可读采用计划

运行：

```bash
make adoption-plan
```

或：

```bash
python tools/stack.py adoption-plan --json
```

即可得到当前 profile 下每个组件的权威仓库、固定 revision、template root / manifest path，以及文件 ownership policy。AI Agent 应依据该计划 fresh-read 上游，再通过 branch / PR 实施；不要直接从 README 猜模板内容。
