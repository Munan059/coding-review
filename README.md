<div align="center">

# 基于 AgentTeams 的多智能体代码审查系统

**一句话定位：用 4 个智能体在 AgentTeams 上跑通「审查 → 修复 → 测试」代码审查闭环，实测 14/14 测试通过**

![framework](https://img.shields.io/badge/framework-AgentTeams-blue) ![language](https://img.shields.io/badge/language-Python-3776AB) ![license](https://img.shields.io/badge/license-MIT-green) ![tests](https://img.shields.io/badge/tests-14%2F14%20passed-brightgreen)

[亮点](#-功能亮点) · [架构](#-架构设计) · [快速开始](#-快速开始) · [目录结构](#-目录结构) · [致谢](#-致谢)

</div>

---

## 📖 这是什么

一个跑在 AgentTeams 框架上的多智能体代码审查系统：顶层由经理（Manager，调度入口）统一接收任务并调度，其下 devteam 团队包含 4 个智能体——协调官（orchestrator / team_leader）负责团队内编排，审查员 / 修复员 / 测试验证员三个执行员并行工作，通过共享状态板对齐上下文，自动完成一次代码审查的端到端闭环。

| 角色      | 名称           | 职责                                  |
| ------- | ------------ | ----------------------------------- |
| 经理（顶层调度入口） | Manager      | 接收任务、统一调度，对外是人机协作的总接口              |
| 协调官（团队 Leader） | orchestrator | 团队内编排：拆解子任务、分派成员、跟踪进度、失败重试、汇总报告 |
| 审查员     | reviewer     | 发现缺陷 / 安全隐患，输出结构化审查报告             |
| 修复员     | fixer        | 按审查意见定位并修改代码                       |
| 测试验证员   | tester       | 编写并运行测试，确认无回归                      |

> **为什么值得一看**：把「人工串行审查」升级为「多智能体并行协作」，过程可追溯、可复用；高风险动作有人工确认与回滚，不自动执行敏感操作。

## ✨ 功能亮点

- **🤖 四智能体闭环** — 审查 → 修复 → 测试 全自动接力，无需人工中转。
- **📋 结构化审查报告** — reviewer 输出带行号、严重级别、复现步骤的报告，fixer 精准定位。
- **🔄 共享状态板** — 所有 Agent 读写同一份上下文，不靠口头传递，不重复不遗漏。
- **🛡 安全边界** — AI 默认只读分析，改代码 / 推送 / 合并需人工确认，全程留痕可审计。
- **✅ 真实跑通** — find_max 案例实测 14/14 测试通过，退出码 0。

## 🏗 架构设计

```
            ┌──────────────────────────────┐
            │  Manager（经理 / 顶层调度入口）  │  接收任务、统一调度
            └──────────────┬───────────────┘
                           ▼
            ┌──────────────────────────────┐
            │ orchestrator（协调官 / Leader）│  团队内拆解 / 分派 / 重试 / 汇总
            └──────────────┬───────────────┘
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
   reviewer            fixer             tester
   (审查)             (修复)           (测试验证)
       │                  │                  │
       └──── 共享状态板（唯一事实源）────┘
```

设计决策：

- **协调官负责制**：单个智能体失败由协调官（orchestrator）自动重试，超阈值降级并转人工接管，不静默放行。
- **上下文结构化**：审查报告、修复差异、测试日志都写入状态板，下游直接读取，避免自然语言转述的误差。
- **最小权限**：审查员对仓库只读，修复员可提交，测试验证员运行代码。

## 🚀 快速开始

本项目的「4 智能体代码审查系统」跑在 **AgentTeams** 平台上（Docker 容器），不是克隆仓库后直接运行。下面两种方式分别说明：方式一是真实使用这套智能体，方式二是本地验证我们提交的演示结果。

### 方式一：用 AgentTeams 运行这套智能体（真实使用）

> 前提：你本机已安装并启动 Docker Desktop（WSL2 后端），且已部署 AgentTeams（一键安装脚本见下）。

1. 打开 Docker Desktop，确认 AgentTeams 相关容器在运行。
2. 浏览器访问控制台：`http://localhost:18080`，用安装时设置的管理员账号登录（Matrix / Element Web）。
3. 把任务发给 **Manager（经理 Agent）**：在 Manager 的对话 / 房间里直接发需求，例如：
   > 请审查这段代码：<粘贴代码或仓库地址>
   Manager 会把它交给 devteam 团队，由协调官（orchestrator）拆解成「审查 → 修复 → 测试」子任务，并和 reviewer / fixer / tester 接力完成。
4. 想看过程或介入时，随时进入对应的 Matrix 房间——人可实时查看、干预、确认 / 回滚（这是 AgentTeams 的 Human-in-the-Loop 设计）。

首次部署 AgentTeams（Windows，系统自带的 PowerShell 即可，无需 7+）：

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; $wc=New-Object Net.WebClient; $wc.Encoding=[Text.Encoding]::UTF8; iex $wc.DownloadString('https://higress.ai/hiclaw/install.ps1')
```

按提示选择中文、模型服务商并填入 API Key 即可，装完自动启动所有容器。

### 方式二：本地验证演示结果（仅跑测试脚本，不启动智能体）

`find_max_demo/` 是这套流水线在 `find_max` 上的端到端实测产物（原始缺陷代码、修复后代码、审查报告、回归测试）。下面这条命令**只运行测试脚本**，用来验证「修复 → 测试」环节的结果，**不会启动那 4 个智能体**：

```bash
git clone https://github.com/Munan059/coding-review.git
cd coding-review/find_max_demo
python test_find_max.py
```

环境要求：Python 3.8+（仅用到标准库 `sys` / `traceback`，无需安装第三方依赖）。

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
