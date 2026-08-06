# agentteams-project（Agent 配置导出）

本文件夹是 **coding-review 多智能体代码审查系统** 的 5 个 Agent 完整配置，
从 **2026-08-05 运行的 AgentTeams 数据卷备份** 中导出，对应目前线上实际跑的版本
（区别于 `项目源码与说明/agentteams-project` 里 8-01 的早期草稿）。

## 包含的 Agent

| 目录 | 角色 | 说明 |
|---|---|---|
| `orchestrator/` | 总指挥 | 派工、共享状态板、终报汇总 |
| `reviewer/` | 审查员 | 代码三维审查（整洁性 / 可用性 / 代码质量） |
| `fixer/` | 修复员 | 按缺陷模式库生成修复代码 |
| `tester/` | 测试员 | 通过 mock 网关调用执行测试 |
| `manager/` | 管理员 | 团队与 Worker 管理（含 `SOUL.top.md` 顶层人设） |

## 每个目录里的文件

- `agent.json` —— Agent 身份、绑定的模型、技能分配
- `SOUL.md` —— Agent 人设与协作纪律（含写操作门禁等）
- `skill.json` —— 该 Agent 的技能清单

## 关于 4 个自定义可复用技能

比赛要求的「可复用 Skill」由 Manager 统一下发，存于 Manager 技能库
（`code-review-3d` / `fix-patterns` / `mock-gateway-protocol` / `shared-state-board`），
不在单个 Worker 的 `skill.json` 清单内；它们已随 8-05 备份一并导出，
可在运行系统的 Manager 技能库中查看。
