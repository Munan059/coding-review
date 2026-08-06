# 审查任务：rank_students 函数

## 背景

用户提交了以下 Python 函数，怀疑存在 bug，请审查：

```python
def rank_students(students=[]):
    ranked = []
    scores = []
    for i in range(1, len(students)):
        student = students[i]
        scores.append(student["score"])
    highest = scores[0]
    for s in scores:
        if s > highest:
            highest = s
    second = None
    for s in scores:
        if s < highest and s > second:
            second = s
    names = []
    for student in students:
        names.append(student["name"])
    passing = 0
    for student in students:
        if student["score"] >= 60:
            passing = passing + 1
    average = sum(scores) / len(scores)
    result = {
        "top": highest,
        "runner_up": second,
        "passed": passing,
        "avg": average,
        "names": names,
    }
    ranked.append(result)
    return ranked[0]
```

函数期望输出：`{"top": 最高分, "runner_up": 第二名分数, "passed": 及格人数(>=60), "avg": 平均分, "names": 全部学生姓名}`。

## 任务要求

1. 静态审查该函数：找出所有问题（bug、边界条件、可变默认参数、副作用、可读性/契约问题）。
2. 对每个问题标注严重度（HIGH / MEDIUM / LOW）并说明影响：哪些输入会导致 IndexError / ZeroDivisionError / TypeError / 错误结果。
3. 给出修复方向建议（不要代替 fixer 写最终代码）。
4. 可运行原始代码验证你的判断，但请保留原始代码文件作为证据。

## 预期产出

- 在 `shared/tasks/rank-students-review-20260805-050346-01/workspace/` 下输出审查报告 `review_report.md`。
- 按 Worker 任务参与规范发布 `shared/tasks/rank-students-review-20260805-050346-01/result.md`，包含 STATUS、SUMMARY、DELIVERABLES。
- 完成后在团队房间 @mention orchestrator 汇报结果。