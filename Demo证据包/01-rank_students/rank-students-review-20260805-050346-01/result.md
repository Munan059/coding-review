STATUS: SUCCESS
SUMMARY: 审查完成：rank_students 存在 3 个高严重度缺陷。HIGH-1：第 4 行 range(1, len(students)) 漏掉第一个学生，scores 不完整致 top/avg 错误（[A:100,B:50] 期望 top=100、avg=75，实际 top=50、avg=50）；HIGH-2：空列表/单元素列表 scores[0] 抛 IndexError、len=0 抛 ZeroDivisionError；HIGH-3：第 12 行 second=None 与 int 比较抛 TypeError（[A:100,B:50,C:80] 实测崩溃）。MEDIUM：可变默认参数 students=[] 反模式；并列最高分时 runner_up=None 语义错误。LOW：avg 基于不完整 scores、ranked 冗余、缺 docstring/KeyError 风险。修复方向：遍历全部学生、入口守卫、second 用 -inf 或排序取第二高分、students=None 哨兵、明确并列契约。原始代码与验证脚本保留在 workspace。

DELIVERABLES:
- shared/tasks/rank-students-review-20260805-050346-01/workspace/review_report.md
- shared/tasks/rank-students-review-20260805-050346-01/workspace/original_rank_students.py
- shared/tasks/rank-students-review-20260805-050346-01/workspace/verify_original.py
