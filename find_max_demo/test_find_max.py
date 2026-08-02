# 测试文件：tester 针对 task-20260801-101600 编写的回归测试
# 覆盖 reviewer 报告的两类严重缺陷 + 正常场景
# 运行：python test_find_max.py
# 预期：14/14 通过，退出码 0（EXIT=0）

import sys
import traceback

# 复用 fixer 修复后的实现
from find_max_修复后 import find_max


def check(name, fn, expect):
    """fn 不抛异常则比对返回值；expect 为异常类型则比对是否抛出该异常。"""
    try:
        got = fn()
    except Exception as e:
        if isinstance(expect, type) and isinstance(e, expect):
            print(f"[PASS] {name} -> 正确抛出 {expect.__name__}")
            return True
        print(f"[FAIL] {name} -> 期望 {expect}，却抛出 {type(e).__name__}: {e}")
        return False
    if isinstance(expect, type):
        print(f"[FAIL] {name} -> 期望抛出 {expect.__name__}，但返回了 {got!r}")
        return False
    if got == expect:
        print(f"[PASS] {name} -> {got}")
        return True
    print(f"[FAIL] {name} -> 期望 {expect}，实际 {got}")
    return False


def run():
    cases = [
        # 正常场景
        ("正序列表", lambda: find_max([1, 2, 3]), 3),
        ("逆序列表", lambda: find_max([3, 2, 1]), 3),
        ("单元素", lambda: find_max([5]), 5),
        ("全零", lambda: find_max([0, 0, 0]), 0),
        ("浮点正常", lambda: find_max([1.5, 2.5, 0.5]), 2.5),
        ("重复最大值", lambda: find_max([10, 10, 5, 10]), 10),
        ("单元素负数", lambda: find_max([-7]), -7),
        ("长列表", lambda: find_max(list(range(1000, 0, -1))), 1000),
        ("全同负数", lambda: find_max([-1, -1]), -1),
        # 缺陷 1：全负数列表不能错误返回 0
        ("全负数[-1,-2,-3]", lambda: find_max([-1, -2, -3]), -1),
        ("全负数[-5,-3,-8]", lambda: find_max([-5, -3, -8]), -3),
        ("浮点负数", lambda: find_max([-2.5, -1.0, -3.0]), -1.0),
        # 缺陷 2：空列表不能静默返回 0，必须抛异常
        ("空列表", lambda: find_max([]), ValueError),
        # 健壮性：混入非数字元素应给清晰报错
        ("混入None", lambda: find_max([1, None, 3]), TypeError),
    ]

    passed = 0
    for name, fn, expect in cases:
        if check(name, fn, expect):
            passed += 1

    total = len(cases)
    print(f"\n==== 测试结果：{passed}/{total} 通过 ====")
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(run())
