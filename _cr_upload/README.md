# Demo 证据包：三个跑到终点的真实运行任务

本证据包汇总 **3 个由四个 Agent（orchestrator / reviewer / fixer / tester）在 AgentTeams 平台真实协作、跑通到终点（G6 完整闭环）** 的代码审查任务。

## 证据来源（真实、非人工编写）

证据来自 AgentTeams 平台运行时**真实产生**的「共享状态板（白板）」与 reviewer/fixer/tester 三阶段文件，从 Docker 数据卷 `agentteams-data` 的卷级备份中**原样导出**：

- 备份文件：`本地运行包\at\agent_snapshot\agentteams-data-backup.tar.gz`（14.7 MB，含 7457 个条目，含四个 Agent 配置与白板数据）
- 复现脚本：`本地运行包\at\extract_demo_evidence.py`（已在本地验证，从备份导出 55 个真实文件：每个任务的 白板状态.json + reviewer 审查报告 + fixer 修复代码 + tester 测试报告 + 任务元数据）

白板 JSON 是四个 Agent 协作留下的**唯一传递通道与最终记录**（reviewer 写 review_report、fixer 写 fixed_code、tester 写 test_report，orchestrator 据其编终报），由平台在 MinIO 对象存储中真实落盘，本包为原始导出，未做任何改写。

## 三个终点任务结果

| 任务（场景） | 被测代码行数 | 审查发现（高/中/低） | 测试结果 | 状态 |
|---|---|---|---|---|
| rank_students | 31 行 | 高 3 / 中 2 / 低 3 | 12/12 全部 PASS | 完成 · G6 |
| process_comments | 28 行 | 高 4 / 中 4 / 低 3（含 XSS 安全漏洞） | 11/11 全部 PASS | 完成 · G6 |
| summarize_orders | 46 行（约 50 行） | 高 4 / 中 3 / 低 5（含 SQL 注入） | 7/7 全部 PASS（含 SQL 注入防护验证，EXIT=0） | 完成 · G6 |

每个子文件夹（`01-rank_students/`、`02-process_comments/`、`03-summarize_orders/`）内含 `白板状态.json`，即该任务共享状态板的原始导出，字段含：
- `task_id` / `scenario_id` / `status`（均为「完成」）/ `current_gate`（均为「G6」）
- `review_report`：reviewer 三维检查法（整洁性 / 可用性 / 代码质量）逐条发现，含行号、严重级别（阻断/警告/提示）与修复建议
- `fixed_code`：fixer 缺陷→修复模式库的实际修复说明与验证结果
- `test_result`：tester 独立回归测试结果与边界实跑数据

## 完整原始文件如何获取

每个任务在平台上还留下了 reviewer 审查报告、fixer 修复代码、tester 测试报告的**完整原始文件**（非摘要）。这些文件可由复现脚本 `extract_demo_evidence.py` 从卷备份一键导出到本文件夹，已在本地验证能正确提取 55 个真实文件。

## 写操作门禁声明（诚实）

本竞赛场景中，commit / push / merge / 删除 / 发布等**写操作绝不自动执行**，仅在用户明确授权时才进行（白板 `ack_status` 字段「待确认 / 已回执 / 已确认 · 不执行写操作」即为佐证）。流水线内只自动完成代码审查、修复、测试与终报，不改写外部仓库。
