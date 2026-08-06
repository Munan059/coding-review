"""summarize_orders 修复结果独立测试脚本（tester）。

测试对象：
    shared/tasks/summarize-orders-review-20260805-061309-02/workspace/fixed_summarize_orders.py

测试目标：
    1. 契约验证（docstring）：total/count/vip_total/top_buyer/flagged/avg/discount_total
    2. 覆盖正常多订单、单元素、空列表、无参、top_buyer 归属、SQL 注入防护、默认参数无污染
    3. 与修复前（原始实现）做对比回归：确认原 bug 可复现、修复后通过
"""

import io
import math
import os
import sys
from contextlib import redirect_stdout

# 修复代码路径（fixer 交付物）
FIXED_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "summarize-orders-review-20260805-061309-02", "workspace",
    )
)
sys.path.insert(0, FIXED_DIR)

from fixed_summarize_orders import summarize_orders as summarize_orders_fixed  # noqa: E402


def O(name, amount, level="normal"):
    return {"name": name, "amount": amount, "level": level}


# ---------------------------------------------------------------------------
# 修复前（原始实现）：与 -01 审查对象一致，用于回归对比。
# send_alert / execute_query 为模块级桩，记录调用，隔离 db 未定义等副作用。
# ---------------------------------------------------------------------------
_calls = {"execute_query": [], "send_alert": []}


def execute_query_stub(q):
    _calls["execute_query"].append(q)


def send_alert_stub(name):
    _calls["send_alert"].append(name)


# 原始实现函数体引用模块级 send_alert / execute_query（原文件定义在模块级），
# 此处提供桩别名，使回归能跑到真实逻辑而不因未定义崩溃
send_alert = send_alert_stub
execute_query = execute_query_stub


def summarize_orders_original(orders, vip_levels=[]):
    result = {"total": 0, "count": 0, "vip_total": 0, "top_buyer": None, "flagged": [], "avg": 0}
    amounts = []
    for i in range(1, len(orders)):
        order = orders[i]
        amounts.append(order["amount"])
    best = amounts[0]
    for a in amounts:
        if a > best:
            best = a
    vip_sum = 0
    for order in orders:
        if order["level"] in vip_levels:
            vip_sum = vip_sum + order["amount"]
    top_name = orders[0]["name"]
    for order in orders:
        if order["amount"] > best:
            top_name = order["name"]
    discount_total = 0
    for order in orders:
        if order["amount"] > 500:
            discount_total = discount_total + order["amount"] * 0.9
        else:
            discount_total = discount_total + order["amount"]
    flagged = []
    for order in orders:
        if order["amount"] > 1000:
            flagged.append(order["name"])
            send_alert(order["name"])
    total = 0
    for order in orders:
        total = total + order["amount"]
    result["total"] = total
    result["count"] = len(orders)
    result["vip_total"] = vip_sum
    result["top_buyer"] = top_name
    result["flagged"] = flagged
    result["discount_total"] = discount_total
    result["avg"] = sum(amounts) / len(amounts)
    query = "SELECT * FROM orders WHERE buyer = '" + top_name + "'"
    execute_query_stub(query)
    return result


# ---------------------------------------------------------------------------
# 用例：描述 + (orders, kwargs) + 期望字典（浮点用 isclose 比较）
# ---------------------------------------------------------------------------
CASES = [
    (
        "正常多订单 [A:1000,B:100,C:2000]",
        ([O("A", 1000), O("B", 100), O("C", 2000)], {}),
        {"total": 3100, "count": 3, "vip_total": 0, "top_buyer": "C",
         "flagged": ["C"], "avg": 3100 / 3, "discount_total": 2800.0},
    ),
    (
        "top_buyer 归属 [A:50,B:1000,C:3000]",
        ([O("A", 50), O("B", 1000), O("C", 3000)], {}),
        {"total": 4050, "count": 3, "vip_total": 0, "top_buyer": "C",
         "flagged": ["C"], "avg": 1350.0, "discount_total": 3650.0},
    ),
    (
        "并列最高取首个 [A:90,B:90]",
        ([O("A", 90), O("B", 90)], {}),
        {"total": 180, "count": 2, "vip_total": 0, "top_buyer": "A",
         "flagged": [], "avg": 90.0, "discount_total": 180.0},
    ),
    (
        "单元素 [A:500]（500 不打折）",
        ([O("A", 500)], {}),
        {"total": 500, "count": 1, "vip_total": 0, "top_buyer": "A",
         "flagged": [], "avg": 500.0, "discount_total": 500.0},
    ),
    (
        "单元素 [A:600]（>500 打 9 折）",
        ([O("A", 600)], {}),
        {"total": 600, "count": 1, "vip_total": 0, "top_buyer": "A",
         "flagged": [], "avg": 600.0, "discount_total": 540.0},
    ),
    (
        "空列表 []",
        ([], {}),
        {"total": 0, "count": 0, "vip_total": 0, "top_buyer": None,
         "flagged": [], "avg": 0.0, "discount_total": 0},
    ),
    (
        "vip_levels 指定 ['gold']",
        ([O("A", 1000, "gold"), O("B", 100, "normal"), O("C", 2000, "gold")],
         {"vip_levels": ["gold"]}),
        {"total": 3100, "count": 3, "vip_total": 3000, "top_buyer": "C",
         "flagged": ["C"], "avg": 3100 / 3, "discount_total": 2800.0},
    ),
]

FAILED = 0


def assert_close(got, expected):
    """逐字段比较：浮点用 isclose，其余严格相等。"""
    if isinstance(expected, float):
        return isinstance(got, (int, float)) and math.isclose(float(got), expected, rel_tol=1e-9, abs_tol=1e-9)
    if isinstance(expected, list):
        return isinstance(got, list) and len(got) == len(expected) and all(
            assert_close(g, e) for g, e in zip(got, expected)
        )
    return got == expected


def run_fixed_case(label, orders, kwargs, expected):
    global FAILED
    try:
        got = summarize_orders_fixed(orders, **kwargs)
        ok = assert_close(got, expected)
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
    print("测试对象: fixed_summarize_orders.py @", FIXED_DIR)

    # 1) 契约用例
    print("\n===== 修复后：契约用例 =====")
    for label, (orders, kwargs), expected in CASES:
        run_fixed_case(label, orders, kwargs, expected)

    # 2) 无参调用两次（MEDIUM-1 默认参数无污染）
    print("\n===== 修复后：默认参数无污染（连续两次 vip_levels 缺省） =====")
    data = [O("A", 1000, "gold"), O("B", 100, "normal")]
    r1 = summarize_orders_fixed(data)
    r2 = summarize_orders_fixed(data)
    if r1 == r2 and r1["vip_total"] == 0:
        print("PASS  两次缺省 vip_levels 调用结果一致且 vip_total=0（无污染）")
    else:
        print(f"FAIL  两次调用异常: r1={r1!r} r2={r2!r}")
        FAILED += 1

    # 3) SQL 注入防护（HIGH-4）：恶意买家名仅作参数传入，不拼进 SQL
    print("\n===== 修复后：SQL 注入防护 =====")
    captured = []
    malicious = "x' OR '1'='1"
    def mock_query(sql, params):
        captured.append((sql, params))
    fix_data = [O("evil' OR '1'='1", 2000), O("B", 100)]
    fix_data[0]["name"] = malicious
    got = summarize_orders_fixed(fix_data, execute_query=mock_query)
    if len(captured) == 1:
        sql, params = captured[0]
        no_inject = (malicious not in sql) and ("?" in sql)
        param_ok = (params == (malicious,)) or (malicious in params)
        print(f"PASS  参数化调用: sql={sql!r} params={params!r}")
        print(f"      sql 不含恶意串（no_inject={no_inject}），恶意名仅入参（param_ok={param_ok}）")
        if not (no_inject and param_ok):
            FAILED += 1
    else:
        print(f"FAIL  execute_query 调用次数异常: {len(captured)}（期望 1）")
        FAILED += 1

    # 4) execute_query 缺省（None）：不执行查询（若实现无条件调用会抛 TypeError）
    print("\n===== 修复后：execute_query 缺省不执行查询 =====")
    try:
        summarize_orders_fixed([O("A", 100)])
        print("PASS  缺省 execute_query 时正常返回（未执行查询，无 TypeError）")
    except Exception as e:  # noqa: BLE001
        print(f"FAIL  缺省 execute_query 异常: {type(e).__name__}: {e}")
        FAILED += 1

    # 5) 无副作用：统计函数不再触发 send_alert 告警输出
    print("\n===== 修复后：无 send_alert 副作用 =====")
    buf = io.StringIO()
    with redirect_stdout(buf):
        summarize_orders_fixed([O("A", 2000), O("B", 3000)])
    if "alert:" not in buf.getvalue():
        print("PASS  调用过程无 alert 输出（send_alert 已解耦）")
    else:
        print(f"FAIL  出现 alert 输出: {buf.getvalue()!r}")
        FAILED += 1

    # 6) 回归对比：原始实现（预期暴露原 bug）
    print("\n===== 回归对比：原始实现（预期暴露原 bug） =====")
    _calls["execute_query"] = []
    _calls["send_alert"] = []
    bug_reproduced = [0]

    def run_original(label, orders, expected):
        try:
            got = summarize_orders_original(orders)
        except Exception as e:  # noqa: BLE001
            print(f"崩溃  [{label}] 原实现抛 {type(e).__name__}: {e}（原 bug 可复现）")
            bug_reproduced[0] += 1
            return
        if not assert_close(got, expected):
            print(f"复现  [{label}] 原实现={got!r}，期望={expected!r}（原 bug 可复现）")
            bug_reproduced[0] += 1
        else:
            print(f"一致  [{label}] 原实现={got!r}（恰好正确）")

    run_original("正常多订单 [A:1000,B:100,C:2000]", [O("A", 1000), O("B", 100), O("C", 2000)],
                 {"total": 3100, "count": 3, "vip_total": 0, "top_buyer": "C",
                  "flagged": ["C"], "avg": 3100 / 3, "discount_total": 2800.0})
    run_original("top_buyer 归属 [A:50,B:1000,C:3000]", [O("A", 50), O("B", 1000), O("C", 3000)],
                 {"total": 4050, "count": 3, "vip_total": 0, "top_buyer": "C",
                  "flagged": ["C"], "avg": 1350.0, "discount_total": 3650.0})
    run_original("单元素 [A:500]", [O("A", 500)],
                 {"total": 500, "count": 1, "vip_total": 0, "top_buyer": "A",
                  "flagged": [], "avg": 500.0, "discount_total": 500.0})
    run_original("空列表 []", [],
                 {"total": 0, "count": 0, "vip_total": 0, "top_buyer": None,
                  "flagged": [], "avg": 0.0, "discount_total": 0})
    # SQL 注入回归：恶意买家名被拼接进 SQL（需两元素订单，原实现 amounts 至少 1 个）
    try:
        evil = [O("x' OR '1'='1", 2000), O("B", 100)]
        summarize_orders_original(evil)
        injected = any("OR" in q.upper() and "'1'='1" in q for q in _calls["execute_query"])
        if injected:
            print(f"复现  [SQL注入] 原实现 SQL 拼接注入: {_calls['execute_query']!r}（原 HIGH-4 bug 可复现）")
            bug_reproduced[0] += 1
        else:
            print(f"一致  [SQL注入] 原实现未注入: {_calls['execute_query']!r}")
    except Exception as e:  # noqa: BLE001
        print(f"崩溃  [SQL注入] 原实现抛 {type(e).__name__}: {e}")
        bug_reproduced[0] += 1
    # send_alert 副作用回归
    if _calls["send_alert"]:
        print(f"复现  [副作用] 原实现触发 send_alert {len(_calls['send_alert'])} 次（原 MEDIUM-2 bug 可复现）")
        bug_reproduced[0] += 1
    else:
        print("一致  [副作用] 原实现未触发 send_alert（恰好无副作用）")

    print(f"\n原 bug 复现次数（修复前暴露的缺陷用例数）: {bug_reproduced[0]}")

    if FAILED:
        print(f"\n测试结果: {FAILED} 项失败 ❌")
        sys.exit(1)
    print("\n测试结果: 全部通过 ✅（修复后行为正确，无回归）")
