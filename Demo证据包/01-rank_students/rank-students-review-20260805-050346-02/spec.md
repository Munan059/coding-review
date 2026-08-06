# 任务：修复 rank_students 函数

## 背景

reviewer 已审查 rank_students（任务 -01），确认 3 个高严重度缺陷：
- HIGH-1：`range(1, len(students))` 漏掉第一个学生，scores 不完整致 top/avg 错误（[A:100,B:50] 期望 top=100、avg=75，实际 top=50、avg=50）；
- HIGH-2：空列表/单元素列表 `scores[0]` 抛 IndexError、len=0 时抛 ZeroDivisionError；
- HIGH-3：`second=None` 与 int 比较抛 TypeError（[A:100,B:50,C:80] 实测崩溃）。
- MEDIUM：可变默认参数 `students=[]` 反模式；并列最高分时 runner_up=None 语义错误。
- LOW：avg 基于不完整 scores、ranked 冗余、缺 docstring/KeyError 风险。

原始代码位于 `shared/tasks/rank-students-review-20260805-050346-01/workspace/original_rank_students.py`，审查报告见 `shared/tasks/rank-students-review-20260805-050346-01/workspace/review_report.md`。

## 预期结果

1. 生成修复后的 `rank_students` 实现，写入 `shared/tasks/rank-students-review-20260805-050346-02/workspace/fixed_rank_students.py`，修复上述 HIGH/MEDIUM/LOW 问题：遍历全部学生、入口守卫（空列表安全处理）、runner_up 用负无穷或排序取第二高分、students 用 None 哨兵、明确并列契约（如最高分并列时 runner_up 可返回 None 或定义为第二个不同分数，请在 docstring 中写明契约）。
2. 编写验证脚本 `workspace/verify_fixed_rank_students.py` 并实测通过（覆盖：正常多学生、单元素、空列表、含并列最高分、分数顺序随机等）。
3. 发布 `shared/tasks/rank-students-review-20260805-050346-02/result.md`，含 STATUS、SUMMARY、DELIVERABLES 及逐项 NOTES（说明 HIGH-1/HIGH-2/HIGH-3/MEDIUM/LOW 的处理方式）。
4. 完成后在当前房间 @mention @orchestrator:matrix-local.agentteams.io:18080 报告结果。