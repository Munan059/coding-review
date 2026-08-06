dpSTATUS: SUCCESS
SUMMARY: 独立测试 rank_students 修复结果：12/12 契约用例全部通过（正常多学生 [A:100,B:50]→top=100/runner_up=50/avg=75.0；三名不同分数 [A:100,B:50,C:80]→runner_up=80 不再 TypeError；单元素/空列表/无参/显式 None 均安全返回；并列最高 runner_up=80、全并列 runner_up=None；60 分算 passed、59 分不算），默认参数无污染检查通过；回归对比确认原实现 11 处缺陷（9 崩溃：TypeError/IndexError + 2 错误结果：漏首学生致 top/avg 错误）全部可复现且修复后全部修复，唯一原本正确的全并列用例输出一致，无回归。测试脚本与测试报告已交付。

DELIVERABLES:
- shared/tasks/rank-students-review-20260805-050346-03/workspace/test_rank_students.py
- shared/tasks/rank-students-review-20260805-050346-03/workspace/test_report.md
