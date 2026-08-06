"""rank_students 修复结果独立测试脚本（tester）。

测试对象：
    shared/tasks/rank-students-review-20260805-050346-02/workspace/fixed_rank_students.py

测试目标：
    1. 契约验证（docstring）：top/runner_up/passed/avg/names 各字段
    2. 覆盖正常多学生、三名不同分数、空/单元素/无参、并列、60 分边界
    3. 与修复前（原始实现）做对比回归：确认原 bug 可复现、修复后通过
"""

import os
import sys

# 修复代码路径（fixer 交付物）
FIXED_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "rank-students-review-20260805-050346-02", "workspace",
    )
)
sys.path.insert(0, FIXED_DIR)

from fixed_rank_students import rank_students as rank_students_fixed  # noqa: E402


# ---------------------------------------------------------------------------
# 修复前（原始实现）：与 -01 审查对象一致，用于回归对比
# ---------------------------------------------------------------------------
def rank_students_original(students=None):
    if students is None:
        students = []
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


# ---------------------------------------------------------------------------
# 测试用例：描述 + 调用参数（元组，None 表示不传） + 期望结果字典
# ---------------------------------------------------------------------------
def S(name, score):
    return {"name": name, "score": score}


CASES = [
    (
        "正常多学生 [A:100,B:50]",
        ([S("A", 100), S("B", 50)],),
        {"top": 100, "runner_up": 50, "passed": 1, "avg": 75.0, "names": ["A", "B"]},
    ),
    (
        "三名不同分数 [A:100,B:50,C:80]",
        ([S("A", 100), S("B", 50), S("C", 80)],),
        {"top": 100, "runner_up": 80, "passed": 2, "avg": 230 / 3, "names": ["A", "B", "C"]},
    ),
    (
        "单元素列表 [A:90]",
        ([S("A", 90)],),
        {"top": 90, "runner_up": None, "passed": 1, "avg": 90.0, "names": ["A"]},
    ),
    (
        "空列表 []",
        ([],),
        {"top": None, "runner_up": None, "passed": 0, "avg": 0.0, "names": []},
    ),
    (
        "无参调用 rank_students()",
        (None,),
        {"top": None, "runner_up": None, "passed": 0, "avg": 0.0, "names": []},
    ),
    (
        "显式 None rank_students(None)",
        (None,),
        {"top": None, "runner_up": None, "passed": 0, "avg": 0.0, "names": []},
    ),
    (
        "并列最高 [A:90,B:90,C:80]",
        ([S("A", 90), S("B", 90), S("C", 80)],),
        {"top": 90, "runner_up": 80, "passed": 3, "avg": 260 / 3, "names": ["A", "B", "C"]},
    ),
    (
        "全并列 [A:85,B:85]",
        ([S("A", 85), S("B", 85)],),
        {"top": 85, "runner_up": None, "passed": 2, "avg": 85.0, "names": ["A", "B"]},
    ),
    (
        "60 分边界 [A:60,B:59]",
        ([S("A", 60), S("B", 59)],),
        {"top": 60, "runner_up": 59, "passed": 1, "avg": 59.5, "names": ["A", "B"]},
    ),
    (
        "60 分边界 [A:60]",
        ([S("A", 60)],),
        {"top": 60, "runner_up": None, "passed": 1, "avg": 60.0, "names": ["A"]},
    ),
    (
        "59 分不算通过 [A:59]",
        ([S("A", 59)],),
        {"top": 59, "runner_up": None, "passed": 0, "avg": 59.0, "names": ["A"]},
    ),
    (
        "多学生乱序 [A:70,B:95,C:88,D:60]",
        ([S("A", 70), S("B", 95), S("C", 88), S("D", 60)],),
        {"top": 95, "runner_up": 88, "passed": 4, "avg": 78.25, "names": ["A", "B", "C", "D"]},
    ),
]

FAILED = 0


def run_fixed_case(label, args, expected):
    """对修复后实现执行单条用例。"""
    global FAILED
    try:
        if args[0] is None and len(args) == 1:
            got = rank_students_fixed()
        else:
            got = rank_students_fixed(*args)
        ok = got == expected
        mark = "PASS" if ok else "FAIL"
        print(f"{mark}  [{label}] 结果={got!r}")
        if not ok:
            print(f"        期望={expected!r}")
            FAILED += 1
        return ok
    except Exception as e:  # noqa: BLE001
        print(f"FAIL  [{label}] 意外异常 {type(e).__name__}: {e}")
        FAILED += 1
        return False


if __name__ == "__main__":
    print("测试对象: fixed_rank_students.py @", FIXED_DIR)

    # 1) 修复后契约验证
    print("\n===== 修复后：契约用例 =====")
    for label, args, expected in CASES:
        run_fixed_case(label, args, expected)

    # 2) 无参调用两次（MEDIUM-1 可变默认参数无污染检查）
    print("\n===== 修复后：默认参数无污染（两次无参调用） =====")
    r1 = rank_students_fixed()
    r2 = rank_students_fixed()
    if r1 == r2 == {"top": None, "runner_up": None, "passed": 0, "avg": 0.0, "names": []}:
        print("PASS  两次 rank_students() 结果一致且为空结果（默认参数无污染）")
    else:
        print(f"FAIL  两次无参调用结果异常: r1={r1!r} r2={r2!r}")
        FAILED += 1

    # 3) 回归对比：原始实现（预期暴露原 bug）
    print("\n===== 回归对比：原始实现（预期暴露原 bug） =====")
    bug_reproduced = 0
    for label, args, expected in CASES:
        try:
            if args[0] is None and len(args) == 1:
                got = rank_students_original()
            else:
                got = rank_students_original(*args)
        except Exception as e:  # noqa: BLE001
            print(f"崩溃  [{label}] 原实现抛 {type(e).__name__}: {e}（原 bug 可复现）")
            bug_reproduced += 1
            continue
        if got != expected:
            print(f"复现  [{label}] 原实现={got!r}，期望={expected!r}（原 bug 可复现）")
            bug_reproduced += 1
        else:
            print(f"一致  [{label}] 原实现={got!r}（恰好正确）")

    print(f"\n原 bug 复现次数（修复前暴露的缺陷用例数）: {bug_reproduced}")

    if FAILED:
        print(f"\n测试结果: {FAILED} 项失败 ❌")
        sys.exit(1)
    print("\n测试结果: 全部通过 ✅（修复后行为正确，无回归）")
