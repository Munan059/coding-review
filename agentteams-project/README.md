# AgentTeams 项目配置（devteam）

本文件夹是从运行中的 AgentTeams 控制器数据库（`agentteams.db`）里导出的**真实项目配置**，也就是本方案的“代码包”。在 AgentTeams 里，**配置即代码**——下面这 6 个 JSON 文件就完整描述了一个 4 智能体协作的代码审查流水线。

> 导出说明：原始数据存于 Kubernetes 风格注册表（kine），每个资源取最新版本；已去掉运行时的噪声字段（`managedFields`、状态里的房间 ID 等），只保留 `metadata`（名字/命名空间）+ `spec`（模型、运行时、技能、人设提示词）。

## 文件清单

| 文件 | 资源类型 | 作用 |
|------|----------|------|
| `team-devteam.json` | Team | 团队定义：描述 + 4 个成员及其角色 |
| `manager-default.json` | Manager | 上层经理：统一调度所有团队，用 deepseek-v4-flash 模型 |
| `worker-orchestrator.json` | Worker | 编排智能体（团队队长），负责任务拆解与分派 |
| `worker-reviewer.json` | Worker | 审查智能体，负责代码问题审查 |
| `worker-fixer.json` | Worker | 修复智能体，负责按审查意见改代码 |
| `worker-tester.json` | Worker | 测试验证智能体，负责跑测试确认修复有效 |

## 四智能体协作流程

```
用户需求
   │
   ▼
Manager（default）── 统一接收任务、创建并调度团队
   │
   ▼
Team: devteam
   │
   ├─ orchestrator（team_leader）── 拆解子任务、分派、跟踪进度、失败重试、汇总报告
   ├─ reviewer    ── 审查代码，产出问题清单
   ├─ fixer      ── 按审查意见修复代码
   └─ tester     ── 运行测试，验证修复是否通过
```

四个 Worker 通过 AgentTeams 的共享状态板互通，orchestrator 做容错与信息对齐，形成“审查 → 修复 → 测试”闭环。

## 各智能体配置要点

| 智能体 | 模型 | 运行时 | 使用的技能（Skill） |
|--------|------|--------|----------------------|
| Manager | deepseek-v4-flash | openclaw | （经理内置调度能力） |
| orchestrator | deepseek-v4-flash | copaw | github-operations、team-coordination、task-management、communication、file-sharing |
| reviewer | deepseek-v4-flash | copaw | git-delegation、github-operations、file-sync |
| fixer | deepseek-v4-flash | copaw | git-delegation、github-operations、file-sync |
| tester | deepseek-v4-flash | copaw | git-delegation、file-sync |

每个 Worker 的 `spec.soul` 字段是该智能体的“人设 / 系统提示词”，定义了它的身份、角色与安全规则（例如：不泄露密钥、只访问任务所需文件）。

## 与比赛要求的对应

- **必选 AgentTeams + Skill**：本配置使用 AgentTeams 框架，并实际挂载了内置 Skill（github-operations、git-delegation、team-coordination、task-management、communication、file-sharing、file-sync）。
- **可运行证据**：`../find_max_demo/` 是这套流水线在 `find_max` 函数上的端到端实测结果（修复两处严重 bug，14/14 测试通过）。

## 复赛复现提示

复赛需在本地或云端起一套 AgentTeams 环境，将上述资源配置应用进去（Team / Manager / 4 个 Worker），并用 `find_max_demo/` 作为输入复现“审查 → 修复 → 测试”闭环。密钥（token / pki 证书）走环境变量，**不进代码仓库**。
