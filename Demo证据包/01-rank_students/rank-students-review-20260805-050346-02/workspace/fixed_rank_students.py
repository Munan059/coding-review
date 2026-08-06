"""修复后的 rank_students 实现。

修复依据：reviewer 审查结论（rank-students-review-20260805-050346-01）
- HIGH-1：原实现 range(1, len(students)) 漏掉第一个学生，scores 不完整。
- HIGH-2：原实现空/单元素列表 scores[0] 抛 IndexError、len=0 抛 ZeroDivisionError。
- HIGH-3：原实现 second=None 与 int 比较抛 TypeError。
- MEDIUM-1：可变默认参数 students=[] 反模式。
- MEDIUM-2：并列最高分时 runner_up 语义未明确。
- LOW：avg 基于不完整 scores、ranked 冗余、缺 docstring/KeyError 风险。
"""


def rank_students(students=None):
    """统计学生成绩并返回排名结果字典。

    Args:
        students: 学生字典列表，每个元素形如 {"name": str, "score": 数值}，
            必须包含 name 与 score 键。默认 None（等价于空列表）。

    Returns:
        结果字典，包含：
        - top: 最高分；空列表时为 None。
        - runner_up: 第二高的【不同】分数；当不存在至少两个不同分数时（
          空列表、单元素、或所有分数并列最高）为 None。
        - passed: 分数 >= 60 的人数。
        - avg: 平均分；空列表时为 0.0。
        - names: 按输入顺序的所有学生姓名。

    Examples:
        >>> rank_students([{"name": "A", "score": 100}, {"name": "B", "score": 50}])
        {'top': 100, 'runner_up': 50, 'passed': 1, 'avg': 75.0, 'names': ['A', 'B']}
    """
    # MEDIUM-1 修复：None 哨兵，避免可变默认参数反模式
    if students is None:
        students = []

    # HIGH-2 修复：空列表安全处理，返回约定空结果（不崩溃）
    if not students:
        return {"top": None, "runner_up": None, "passed": 0, "avg": 0.0, "names": []}

    # HIGH-1 修复：遍历全部学生，不再漏掉第一个
    scores = [s["score"] for s in students]
    names = [s["name"] for s in students]

    top = max(scores)

    # HIGH-3/MEDIUM-2 修复：基于唯一分数集合取第二高【不同】分数；
    # 不足两个不同分数（含并列最高）时 runner_up 为 None，契约见 docstring。
    distinct_scores = sorted(set(scores))
    runner_up = distinct_scores[-2] if len(distinct_scores) >= 2 else None

    passed = sum(1 for s in scores if s >= 60)
    avg = sum(scores) / len(scores)

    # LOW 修复：去掉冗余 ranked 列表，直接返回结果
    return {
        "top": top,
        "runner_up": runner_up,
        "passed": passed,
        "avg": avg,
        "names": names,
    }
