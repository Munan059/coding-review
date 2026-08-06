"""验证修复后的 rank_students 行为（覆盖正常/单元素/空/并列/顺序随机等）。"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixed_rank_students import rank_students


def close(a, b, eps=1e-9):
    return abs(a - b) < eps


def check(desc, got, expected):
    ok = (
        got["top"] == expected["top"]
        and got["runner_up"] == expected["runner_up"]
        and got["passed"] == expected["passed"]
        and close(got["avg"], expected["avg"])
        and got["names"] == expected["names"]
    )
    print(f"{'PASS' if ok else 'FAIL'}  {desc}: {got}")
    return ok


failed = 0

# 1. 正常多学生（含 HIGH-3 场景）
ok = check(
    "正常多学生 [A:100,B:50,C:80]",
    rank_students([{"name": "A", "score": 100}, {"name": "B", "score": 50}, {"name": "C", "score": 80}]),
    {"top": 100, "runner_up": 80, "passed": 2, "avg": 76.66666666666667, "names": ["A", "B", "C"]},
)
failed += 0 if ok else 1

# 2. 两元素不同分（HIGH-1 场景：原实现 top/avg 错误）
ok = check(
    "两元素不同分 [A:100,B:50]",
    rank_students([{"name": "A", "score": 100}, {"name": "B", "score": 50}]),
    {"top": 100, "runner_up": 50, "passed": 1, "avg": 75.0, "names": ["A", "B"]},
)
failed += 0 if ok else 1

# 3. 单元素（HIGH-2 场景：原实现 IndexError）
ok = check(
    "单元素 [A:100]",
    rank_students([{"name": "A", "score": 100}]),
    {"top": 100, "runner_up": None, "passed": 1, "avg": 100.0, "names": ["A"]},
)
failed += 0 if ok else 1

# 4. 空列表（HIGH-2 场景：原实现 IndexError/ZeroDivisionError）
ok = check(
    "空列表 []",
    rank_students([]),
    {"top": None, "runner_up": None, "passed": 0, "avg": 0.0, "names": []},
)
failed += 0 if ok else 1

# 5. 含并列最高分（MEDIUM-2 场景：runner_up 取第二不同分数 80）
ok = check(
    "含并列最高分 [A:90,B:90,C:80]",
    rank_students([{"name": "A", "score": 90}, {"name": "B", "score": 90}, {"name": "C", "score": 80}]),
    {"top": 90, "runner_up": 80, "passed": 3, "avg": 86.66666666666667, "names": ["A", "B", "C"]},
)
failed += 0 if ok else 1

# 6. 全部相同分（MEDIUM-2 场景：runner_up=None）
ok = check(
    "全相同分 [A:90,B:90,C:90]",
    rank_students([{"name": "A", "score": 90}, {"name": "B", "score": 90}, {"name": "C", "score": 90}]),
    {"top": 90, "runner_up": None, "passed": 3, "avg": 90.0, "names": ["A", "B", "C"]},
)
failed += 0 if ok else 1

# 7. 分数顺序随机（验证与顺序无关）
ok = check(
    "顺序随机 [A:50,B:100,C:75]",
    rank_students([{"name": "A", "score": 50}, {"name": "B", "score": 100}, {"name": "C", "score": 75}]),
    {"top": 100, "runner_up": 75, "passed": 2, "avg": 75.0, "names": ["A", "B", "C"]},
)
failed += 0 if ok else 1

# 8. 无参调用（MEDIUM-1 场景：students=None 哨兵，等价空列表且不崩溃）
ok = check("无参调用 rank_students()", rank_students(), {"top": None, "runner_up": None, "passed": 0, "avg": 0.0, "names": []})
failed += 0 if ok else 1

# 9. 默认参数不共享状态：连续两次无参调用结果一致且互不影响
r1 = rank_students()
r2 = rank_students()
if r1 == r2 and r1["names"] == []:
    print("PASS  默认参数无跨调用污染")
else:
    print("FAIL  默认参数跨调用污染")
    failed += 1

if failed:
    print(f"\n{failed} 项验证失败")
    sys.exit(1)
print("\n全部验证通过")
