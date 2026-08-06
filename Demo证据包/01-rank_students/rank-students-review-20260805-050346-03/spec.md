# 任务：测试 rank_students 修复结果

## 背景

reviewer 已审查 rank_students（任务 -01）确认缺陷，fixer 已完成修复（任务 -02），修复代码位于 `shared/tasks/rank-students-review-20260805-050346-02/workspace/fixed_rank_students.py`。本次任务由你（tester）独立验证修复后行为正确且无回归。

修复后的契约（以 fixed_rank_students.py docstring 为准）：
- top：最高分；空列表为 None
- runner_up：第二高的【不同】分数；不存在至少两个不同分数时为 None
- passed：分数 >= 60 的人数
- avg：平均分；空列表为 0.0
- names：按输入顺序的所有学生姓名
- 签名 `rank_students(students=None)`，None 等价空列表

## 预期结果

1. 读取修复代码，设计并运行覆盖以下场景的测试用例：
   - 正常多学生（如 [A:100,B:50] → top=100、runner_up=50、passed=1、avg=75.0、names=[A,B]）
   - 三名不同分数（如 [A:100,B:50,C:80] → runner_up=80，不再 TypeError）
   - 单元素列表、空列表、无参调用（不崩溃）
   - 并列最高（如 [A:90,B:90,C:80] → runner_up=80）、全并列（runner_up=None）
   - 分数边界（60 分算 passed、59 分不算）
2. 若可能，用原始（修复前）代码做对比回归，确认原 bug 可复现、修复后通过。原始代码位于 `shared/tasks/rank-students-review-20260805-050346-01/workspace/original_rank_students.py`。
3. 将测试脚本与测试报告写入 `shared/tasks/rank-students-review-20260805-050346-03/workspace/`，发布 `shared/tasks/rank-students-review-20260805-050346-03/result.md`，含 STATUS、SUMMARY、DELIVERABLES，必要时加 NOTES。
4. 完成后在当前房间 @mention @orchestrator:matrix-local.agentteams.io:18080 报告结果。