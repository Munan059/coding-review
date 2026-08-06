# Demo 证据包（端到端跑通记录）

本文件夹是「基于 AgentTeams 的多智能体代码审查系统」参赛项目的**运行证据包**，证明四个智能体（审查员 / 修复员 / 测试验证员 / 协调官）在 AgentTeams 平台上真实协作、跑通「审查 → 修复 → 测试」闭环。

## 一、跑到终点的任务（G6 完整闭环）

三个任务在平台上真实运行至最终汇总关卡（G6），共享状态板原始记录如下：

| 任务 | 被测代码 | 审查发现 | 测试结果 | 状态 |
|------|---------|---------|---------|------|
| rank_students | 31 行 | 高 3 / 中 2 / 低 3 | 12/12 | 完成 · G6 |
| process_comments | 28 行 | 高 4 / 中 4 / 低 3（含 XSS） | 11/11 | 完成 · G6 |
| summarize_orders | 46 行 | 高 4 / 中 3 / 低 5（含 SQL 注入） | 7/7（EXIT=0） | 完成 · G6 |

每个任务目录下的 `白板状态.json` 是四个 Agent 协作留下的**共享状态板原始导出**（字段含 `status=完成`、`current_gate=G6`、`review_report`、`fixed_code`、`test_result`），从 Docker 卷备份原样提取，非人工编写。

## 二、项目源码与说明

`项目源码与说明/` 子文件夹包含本项目的 AgentTeams 配置（`agentteams-project/`）与早期端到端演示（`find_max_demo/`），详见该子文件夹内的 README。

## 三、证据来源与诚实声明

- 白板 JSON 提取自本地 Docker 卷全量备份 `本地运行包/at/agent_snapshot/agentteams-data-backup.tar.gz`（MinIO 内联存储，已校验完整）。
- 写操作门禁：commit / push / merge 等敏感操作不自动执行，需人工确认——本证据包仅记录分析、修复、测试过程，未含任何未经授权的写操作。
