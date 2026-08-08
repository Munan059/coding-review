<div align="center">

# 基于 AgentTeams 的多智能体代码审查系统

**一句话定位：用 4 个业务智能体（orchestrator / reviewer / fixer / tester）在 AgentTeams 上跑通「审查 → 修复 → 测试」闭环，三个真实任务全部跑通至 G6 汇总关卡，含安全用例 7/7 通过**

![framework](https://img.shields.io/badge/framework-AgentTeams-blue) ![language](https://img.shields.io/badge/language-Python-3776AB) ![license](https://img.shields.io/badge/license-MIT-green) ![tests](https://img.shields.io/badge/tests-7%2F7%20passed-brightgreen)

[亮点](#-功能亮点) · [架构](#-架构设计) · [快速开始](#-快速开始) · [目录结构](#-目录结构) · [致谢](#-致谢)

</div>

---

## 📖 这是什么

一个跑在 AgentTeams 框架上的多智能体代码审查系统：平台默认的管理员（Manager）作为顶层调度入口统一接收任务，其下 `coding-review` 团队包含 4 个业务智能体——协调官（orchestrator）负责团队内编排，审查员 / 修复员 / 测试验证员三个执行员并行工作，通过共享状态板对齐上下文，自动完成一次代码审查的端到端闭环。

| 角色 | 名称 | 职责 |
| --- | --- | --- |
| 管理员（顶层调度入口） | Manager | 接收任务、统一调度，对外是人机协作的总接口 |
| 协调官（团队 Leader） | orchestrator | 团队内编排：拆解子任务、分派成员、跟踪进度、失败重试、汇总报告 |
| 审查员 | reviewer | 发现缺陷 / 安全隐患，输出结构化审查报告 |
| 修复员 | fixer | 按审查意见与缺陷模式库定位并修改代码 |
| 测试验证员 | tester | 通过 mock 网关调用执行测试，确认无回归 |

> **为什么值得一看**：把「人工串行审查」升级为「多智能体并行协作」，过程可追溯、可复用；高风险动作有人工确认与回滚，不自动执行敏感操作。本仓库附带三个真实任务从审查到测试全过程的运行证据（共享状态板原始导出），而非演示用的玩具样例。

## ✨ 功能亮点

- **🤖 四智能体闭环** — 审查 → 修复 → 测试 全自动接力，无需人工中转。
- **📋 结构化审查报告** — reviewer 输出带行号、严重级别、复现步骤的报告，fixer 精准定位。
- **🔄 共享状态板** — 所有 Agent 读写同一份上下文（落地为 `shared/state-board/{task_id}.json`），不靠口头传递，不重复不遗漏。
- **🛡 安全边界** — AI 默认只读分析，改代码 / 推送 / 合并需人工确认，全程留痕可审计。
- **✅ 真实跑通** — 三个真实任务（rank_students / process_comments / summarize_orders）全部 G6 闭环，其中安全用例 7/7 通过，退出码均为 0。
- **🧩 四个可复用 Skill** — 比赛要求的「可复用 Skill」由 Manager 统一下发：`code-review-3d`（审查三维法）/ `fix-patterns`（缺陷→修复模式库）/ `mock-gateway-protocol`（mock 网关调用协议）/ `shared-state-board`（共享状态板与终报规范）。

## 🏗 架构设计

```
            ┌──────────────────────────────┐
            │  Manager（管理员 / 顶层调度入口） │  接收任务、统一调度
            └──────────────┬───────────────┘
                           ▼
            ┌──────────────────────────────┐
            │  coding-review 团队            │
            │ orchestrator（协调官 / Leader）│  团队内拆解 / 分派 / 重试 / 汇总
            └──────────────┬───────────────┘
       ┌──────────────────┼──────────────────┐
       ▼                  ▼                  ▼
   reviewer            fixer             tester
   (审查)             (修复)           (测试验证)
       │                  │                  │
       └──── 共享状态板 shared/state-board/{task_id}.json（唯一事实源）────┘
```

设计决策：

- **协调官负责制**：单个智能体失败由协调官（orchestrator）自动重试，超阈值降级并转人工接管，不静默放行。
- **上下文结构化**：审查报告、修复差异、测试日志都写入状态板，下游直接读取，避免自然语言转述的误差。
- **最小权限**：审查员对仓库只读，修复员可提交，测试验证员运行代码。
- **四个可复用 Skill 由 Manager 下发**：每个业务 Agent 各绑定一个团队自研技能，与运行时内置技能互补，满足比赛「必须设计可复用 Skill」的硬指标。

## 🚀 快速开始

本项目的「4 智能体代码审查系统」跑在 **AgentTeams** 平台上（Docker 容器），不是克隆仓库后直接运行。下面两种方式分别说明：方式一是真实使用这套智能体，方式二是在本地复现我们提交的演示测试结果。

### 方式一：用 AgentTeams 运行这套智能体（真实使用）

> 前提：你本机已安装并启动 Docker Desktop（WSL2 后端），且已部署 AgentTeams。

1. 打开 Docker Desktop，确认 AgentTeams 相关容器在运行。
2. 浏览器访问控制台：`http://localhost:18080`，用安装时设置的管理员账号登录（Matrix / Element Web）。
3. 把任务发给 **Manager（管理员 Agent）**：在 Manager 的对话 / 房间里直接发需求，例如：
   > 请审查这段代码：<粘贴代码或仓库地址>
   Manager 会把它交给 `coding-review` 团队，由协调官（orchestrator）拆解成「审查 → 修复 → 测试」子任务，并和 reviewer / fixer / tester 接力完成。
4. 想看过程或介入时，随时进入对应的 Matrix 房间——人可实时查看、干预、确认 / 回滚（这是 AgentTeams 的 Human-in-the-Loop 设计）。

首次部署 AgentTeams（Windows，推荐使用官方 **bash 安装脚本**在 WSL2 Ubuntu 终端中执行 `bash agentteams-install.sh`，配 Docker Desktop；旧版 PowerShell 一键安装器功能不全已弃用）：

```bash
# 在 WSL2 Ubuntu 终端中
bash agentteams-install.sh
```

按提示选择中文、模型服务商并填入 API Key 即可，装完自动启动所有容器。完整团队配置（`coding-review` 团队的 5 个 Agent 定义）见本仓库 `Demo证据包/agentteams-project/`。

### 方式二：本地复现演示测试结果（仅跑测试脚本，不启动智能体）

`Demo证据包/` 下三个任务各包含 reviewer / fixer / tester 的真实产物（原始代码、修复后代码、审查报告、测试脚本、测试报告、共享状态板导出）。下面命令**只运行 tester 留下的测试脚本**，用来验证「修复 → 测试」环节的结果，**不会启动那 4 个智能体**：

```bash
git clone https://github.com/Munan059/coding-review.git
cd coding-review

# 任务一：rank_students（12/12 通过，EXIT=0）
python3 "Demo证据包/01-rank_students/rank-students-review-20260805-050346-03/workspace/test_rank_students.py"

# 任务二：process_comments（11/11 通过，EXIT=0）
python3 "Demo证据包/02-process_comments/process-comments-review-20260805-083607-03/workspace/test_process_comments.py"

# 任务三：summarize_orders（7/7 通过，含 SQL 注入防护，EXIT=0）
python3 "Demo证据包/03-summarize_orders/summarize-orders-review-20260805-061309-03/workspace/test_summarize_orders.py"
```

环境要求：Python 3.8+（仅用到标准库，无需安装第三方依赖）。每个测试脚本通过相对路径加载 fixer 实际交付的修复代码，保证测试对象真实。

预期输出（以 rank_students 为例）：

```
===== 修复后：契约用例 =====
PASS  [正常多学生 [A:100,B:50]] 结果=...
...
测试结果: 全部通过 ✅（修复后行为正确，无回归）
```

进程退出码为 0，即代表该任务在「修复 → 测试」环节的真实运行结果（完整「审查 → 修复 → 测试」由 AgentTeams 内四智能体协作完成，详见架构与目录）。

## 📂 目录结构

```
coding-review/
├── README.md
├── LICENSE
├── .gitignore
└── Demo证据包/                      # 端到端跑通的运行证据包
    ├── README.md                    # 证据包总说明（三任务 G6 闭环汇总）
    ├── agentteams-project/          # coding-review 团队的 5 个 Agent 配置（从运行环境导出）
    │   ├── README.md                # 配置说明与四智能体协作流程
    │   ├── manager/                 # 管理员：SOUL.md / SOUL.top.md / agent.json / skill.json
    │   ├── orchestrator/            # 协调官：SOUL.md / agent.json / skill.json
    │   ├── reviewer/                # 审查员
    │   ├── fixer/                   # 修复员
    │   └── tester/                  # 测试验证员
    ├── 01-rank_students/            # 任务一（31 行，12/12 测试通过）
    │   ├── 白板状态.json             # 共享状态板原始导出（status=完成 / current_gate=G6）
    │   ├── rank-students-review-20260805-050346-01/  # 审查阶段产物
    │   │   ├── meta.json / spec.md / result.md
    │   │   └── workspace/           # original_rank_students.py / review_report.md / verify_original.py
    │   ├── rank-students-review-20260805-050346-02/  # 修复阶段产物
    │   │   └── workspace/           # fixed_rank_students.py / verify_fixed_rank_students.py
    │   └── rank-students-review-20260805-050346-03/  # 测试阶段产物
    │       └── workspace/           # test_rank_students.py / test_report.md
    ├── 02-process_comments/         # 任务二（28 行，11/11 测试通过，含 XSS 修复）
    └── 03-summarize_orders/         # 任务三（46 行，7/7 测试通过，含 SQL 注入防护）
```

## 🕳 工程踩坑精选（来自三个真实任务）

| 任务 | 坑 | 现象 | 结论 |
| --- | --- | --- | --- |
| rank_students | 漏掉第一个学生 | 遍历从 `range(1, n)` 开始，最高分 / 平均分算错 | 遍历全部元素收集分数 |
| rank_students | 空 / 单元素崩溃 | `scores[0]` 越界抛 IndexError | 空列表守卫 + 单元素正常计算 |
| rank_students | runner_up 比较 None | `second=None` 与 int 比较抛 TypeError | 用 `sorted(set(scores))` 取第二高不同分数 |
| process_comments | XSS 注入 | 用户内容未转义直接拼进输出 | 输出前做 HTML 转义 |
| summarize_orders | 漏首订单致 avg 错误 | 同上 `range(1, n)` 思维，top_buyer 恒为首单 | 遍历全部订单 + `max(orders, key=amount)` |
| summarize_orders | SQL 字符串拼接注入 | `buyer = 'x' OR '1'='1'` 直接拼接 | 参数化查询 `?` + 参数分离 |

## 🙏 致谢

- [AgentTeams](https://hiclaw.io) — 多智能体协同框架，本系统的协同设计基点。
- 新智基座 / Agent Infra 赛道主办方 — 提供比赛平台与评审反馈。

<div align="center">觉得有用点个 ⭐</div>

---

本项目采用 [MIT 许可证](LICENSE)。

## 📅 更新记录

- 2026-08-08 重写 README：对齐 8-05 正式配置与「Demo证据包」真实结构（三个 G6 闭环任务 + 5 Agent 配置），团队名统一为 `coding-review`，修正已废弃的 PowerShell 安装命令；徽章以安全用例 7/7 为代表（三任务实测 12/12、11/11、7/7，合计 30/30，明细保留）。
- 2026-08-06 完成初赛作品提交（作品简介 / 方案 PPT / Demo 证据包已备齐并上传官网）。
