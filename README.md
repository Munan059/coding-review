<div align="center">

# 基于 AgentTeams 的多智能体代码审查系统

**一句话定位：用 4 个智能体在 AgentTeams 上跑通「审查 → 修复 → 测试」代码审查闭环，实测 14/14 测试通过**

![framework](https://img.shields.io/badge/framework-AgentTeams-blue)

![language](https://img.shields.io/badge/language-Python-3776AB)

![license](https://img.shields.io/badge/license-MIT-green)



![tests](https://img.shields.io/badge/tests-14%2F14%20passed-brightgreen)

![track](https://img.shields.io/badge/track-Agent%20Infra%20%2F%20新智基座-orange)

[亮点](#-功能亮点) · [架构](#-架构设计) · [快速开始](#-快速开始) · [目录结构](#-目录结构) · [致谢](#-致谢)

</div>

---

## 📖 这是什么

一个跑在 AgentTeams 框架上的多智能体代码审查系统：由 1 个经理（orchestrator）统一调度 3 个执行员（审查 / 修复 / 测试），通过共享状态板对齐上下文，自动完成一次代码审查的端到端闭环。

| 角色    | 名称           | 职责                    |
| ----- | ------------ | --------------------- |
| 经理    | orchestrator | 拆解任务、调度成员、失败重试、汇总报告   |
| 审查员   | reviewer     | 发现缺陷 / 安全隐患，输出结构化审查报告 |
| 修复员   | fixer        | 按审查意见定位并修改代码          |
| 测试验证员 | tester       | 编写并运行测试，确认无回归         |

> **为什么值得一看**：把「人工串行审查」升级为「多智能体并行协作」，过程可追溯、可复用；高风险动作有人工确认与回滚，不自动执行敏感操作。

## ✨ 功能亮点

- **🤖 四智能体闭环** — 审查 → 修复 → 测试 全自动接力，无需人工中转。
- **📋 结构化审查报告** — reviewer 输出带行号、严重级别、复现步骤的报告，fixer 精准定位。
- **🔄 共享状态板** — 所有 Agent 读写同一份上下文，不靠口头传递，不重复不遗漏。
- **🛡 安全边界** — AI 默认只读分析，改代码 / 推送 / 合并需人工确认，全程留痕可审计。
- **✅ 真实跑通** — find_max 案例实测 14/14 测试通过，退出码 0。

## 🏗 架构设计

```
            ┌──────────────────┐
            │   orchestrator   │  经理：拆解 / 调度 / 重试 / 汇总
            └────────┬─────────┘
       ┌────────────┼────────────┐
       ▼            ▼            ▼
   reviewer       fixer        tester
   (审查)        (修复)       (测试验证)
       │            │            │
       └──── 共享状态板（唯一事实源）────┘
```

设计决策：

- **经理负责制**：单个智能体失败由经理自动重试，超阈值降级并转人工接管，不静默放行。
- **上下文结构化**：审查报告、修复差异、测试日志都写入状态板，下游直接读取，避免自然语言转述的误差。
- **最小权限**：审查员对仓库只读，修复员可提交，测试验证员运行代码。

## 🚀 快速开始

### 环境要求

- Python 3.8+（仅用到标准库 `sys` / `traceback`，无需安装第三方依赖）

### 运行端到端验证案例（find_max）

```bash
git clone https://github.com/Munan059/coding-review.git
cd coding-review/find_max_demo
python test_find_max.py
```

预期输出：

```
==== 测试结果：14/14 通过 ====
```

进程退出码为 0，即代表流水线在「修复 → 测试」环节的真实运行结果（完整「审查 → 修复 → 测试」由 AgentTeams 内四智能体协作完成，详见架构与目录）。

## 📂 目录结构

```
coding-review/
├── README.md
├── LICENSE
├── find_max_demo/            # 端到端验证案例（可直接运行）
│   ├── find_max_原始.py       # 含 2 个严重缺陷的原始代码
│   ├── find_max_修复后.py     # fixer 按审查报告修复后的版本
│   ├── test_find_max.py       # tester 编写的回归测试（14/14）
│   ├── review_report.md       # reviewer 输出的结构化审查报告
│   └── test_output.txt        # 测试真实运行结果（退出码 0）
└── agentteams-project/       # AgentTeams 项目配置（从运行环境导出，即“代码包”）
    ├── team-devteam.json       # 团队定义：4 智能体成员与角色
    ├── manager-default.json    # 经理：统一调度，deepseek-v4-flash
    ├── worker-orchestrator.json # 编排（队长）：拆解/分派/重试/汇总
    ├── worker-reviewer.json    # 审查智能体
    ├── worker-fixer.json       # 修复智能体
    ├── worker-tester.json      # 测试验证智能体
    └── README.md               # 配置说明与四智能体协作流程
```

## 🕳 工程踩坑精选

| 坑        | 现象                    | 结论                           |
| -------- | --------------------- | ---------------------------- |
| 极值初值写死 0 | 全负数列表错误返回 0           | 极值初值应取 `nums[0]`             |
| 空列表未处理   | 空列表静默返回 0             | 显式 `raise ValueError`，尽早暴露错误 |
| 类型异常提示晦涩 | 混入 None 抛原始 TypeError | 比较前做类型校验，给清晰报错               |

## 🙏 致谢

- [AgentTeams](https://hiclaw.io) — 多智能体协同框架，本系统的协同设计基点。
- 新智基座 / Agent Infra 赛道主办方 — 提供比赛平台与评审反馈。

<div align="center">觉得有用点个 ⭐</div>

---

本项目采用 [MIT 许可证](LICENSE)。
