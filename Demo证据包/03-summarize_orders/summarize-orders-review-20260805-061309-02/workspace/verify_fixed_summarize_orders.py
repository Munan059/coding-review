"""验证修复后的 summarize_orders 行为（覆盖正常/单元素/空/top_buyer/SQL 注入/无参等）。"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixed_summarize_orders import summarize_orders


def close(a, b, eps=1e-9):
    return abs(a - b) < eps


def check(desc, got, expected):
    ok = (
        got["total"] == expected["total"]
        and got["count"] == expected["count"]
        and got["vip_total"] == expected["vip_total"]
        and got["top_buyer"] == expected["top_buyer"]
        and got["flagged"] == expected["flagged"]
        and close(got["avg"], expected["avg"])
        and close(got["discount_total"], expected["discount_total"])
    )
    print(f"{'PASS' if ok else 'FAIL'}  {desc}: {got}")
    return ok


failed = 0

# 1. 正常多订单（HIGH-1 场景：avg 含第一个订单；HIGH-3 场景：top_buyer=C）
ok = check(
    "正常多订单 [A:1000,B:100,C:2000]",
    summarize_orders(
        [
            {"name": "A", "amount": 1000, "level": "gold"},
            {"name": "B", "amount": 100, "level": "normal"},
            {"name": "C", "amount": 2000, "level": "gold"},
        ],
        vip_levels=["gold"],
    ),
    {
        "total": 3100,
        "count": 3,
        "vip_total": 3000,
        "top_buyer": "C",
        "flagged": ["C"],
        "avg": 1033.3333333333333,
        "discount_total": 900.0 + 100.0 + 1800.0,  # A/C 打 9 折，B 原价；A=1000 不 >1000 不进 flagged
    },
)
failed += 0 if ok else 1

# 2. 单元素（HIGH-2 场景：原实现 IndexError）
ok = check(
    "单元素 [A:100]",
    summarize_orders([{"name": "A", "amount": 100, "level": "normal"}]),
    {
        "total": 100,
        "count": 1,
        "vip_total": 0,
        "top_buyer": "A",
        "flagged": [],
        "avg": 100.0,
        "discount_total": 100.0,
    },
)
failed += 0 if ok else 1

# 3. 空列表（HIGH-2 场景：原实现 IndexError/ZeroDivisionError）
ok = check(
    "空列表 []",
    summarize_orders([]),
    {"total": 0, "count": 0, "vip_total": 0, "top_buyer": None, "flagged": [], "avg": 0.0, "discount_total": 0},
)
failed += 0 if ok else 1

# 4. top_buyer 归属（HIGH-3 场景：最高金额 C，原实现返回 A）
ok = check(
    "top_buyer 归属 [A:50,B:1000,C:3000]",
    summarize_orders(
        [
            {"name": "A", "amount": 50, "level": "normal"},
            {"name": "B", "amount": 1000, "level": "normal"},
            {"name": "C", "amount": 3000, "level": "normal"},
        ]
    ),
    {
        "total": 4050,
        "count": 3,
        "vip_total": 0,
        "top_buyer": "C",
        "flagged": ["C"],  # B=1000 不 >1000，不进 flagged
        "avg": 1350.0,
        "discount_total": 50.0 + 900.0 + 2700.0,
    },
)
failed += 0 if ok else 1

# 5. SQL 注入防护（HIGH-4 场景：参数化查询，恶意买家名不进 SQL 语句）
captured = {}
def fake_execute_query(sql, params):
    captured["sql"] = sql
    captured["params"] = params

malicious = {"name": "x' OR '1'='1", "amount": 9999, "level": "normal"}
summarize_orders([malicious], execute_query=fake_execute_query)
sql_ok = captured["sql"] == "SELECT * FROM orders WHERE buyer = ?" and captured["params"] == ("x' OR '1'='1",)
if sql_ok:
    print(f"PASS  SQL 参数化查询: sql={captured['sql']!r}, params={captured['params']!r}")
else:
    print(f"FAIL  SQL 参数化查询: sql={captured['sql']!r}, params={captured['params']!r}")
    failed += 1

# 6. 无参调用（MEDIUM-1 场景：vip_levels 默认 None，等价空集合且不崩溃）
ok = check(
    "无参 vip_levels [A:100,B:200]",
    summarize_orders(
        [
            {"name": "A", "amount": 100, "level": "gold"},
            {"name": "B", "amount": 200, "level": "normal"},
        ]
    ),
    {
        "total": 300,
        "count": 2,
        "vip_total": 0,
        "top_buyer": "B",
        "flagged": [],
        "avg": 150.0,
        "discount_total": 100.0 + 200.0,
    },
)
failed += 0 if ok else 1

# 7. 默认参数不共享状态：连续两次无参 vip_levels 调用结果一致且互不影响
r1 = summarize_orders([{"name": "A", "amount": 100, "level": "gold"}])
r2 = summarize_orders([{"name": "A", "amount": 100, "level": "gold"}])
if r1 == r2:
    print("PASS  默认参数无跨调用污染")
else:
    print("FAIL  默认参数跨调用污染")
    failed += 1

if failed:
    print(f"\n{failed} 项验证失败")
    sys.exit(1)
print("\n全部验证通过")
