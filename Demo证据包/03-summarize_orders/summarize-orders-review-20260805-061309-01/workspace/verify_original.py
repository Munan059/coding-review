"""验证脚本：对原始 summarize_orders 进行边界/逻辑验证。

对外部依赖打桩：
- send_alert: 记录调用，不打印
- db.run / execute_query: 记录 SQL，返回 None
"""

# ---- 打桩外部依赖 ----
alert_calls = []
sql_calls = []


def send_alert(name):
    alert_calls.append(name)


class _FakeDB:
    def run(self, q):
        sql_calls.append(q)
        return []


db = _FakeDB()


def summarize_orders(orders, vip_levels=[]):
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
    execute_query(query)
    return result


def execute_query(q):
    return db.run(q)


def run_case(name, orders, vip_levels=None, expect=None):
    alert_calls.clear()
    sql_calls.clear()
    try:
        out = summarize_orders(orders, vip_levels if vip_levels is not None else [])
        status = "PASS" if (expect is None or out == expect) else "FAIL"
        detail = "" if status == "PASS" else f"  期望: {expect}"
        print(f"{name:<40} -> {status}  {out}{detail}")
        if alert_calls:
            print(f"    send_alert 调用: {alert_calls}")
        if sql_calls:
            print(f"    execute_query SQL: {sql_calls}")
    except Exception as e:
        print(f"{name:<40} -> EXCEPTION {type(e).__name__}: {e}")


print("===== 边界/异常场景 =====")
run_case("空列表 []", [])
run_case("单元素 [A:100]", [{"name": "A", "amount": 100, "level": "gold"}])

print("\n===== 漏掉第一个订单验证 =====")
# 期望 top_buyer=C（最高金额 2000），avg=(1000+2000)/2=1500，total=3100
orders1 = [
    {"name": "A", "amount": 1000, "level": "gold"},
    {"name": "B", "amount": 100, "level": "normal"},
    {"name": "C", "amount": 2000, "level": "vip"},
]
expect1 = {
    "total": 3100,
    "count": 3,
    "vip_total": 2000,
    "top_buyer": "C",
    "flagged": ["C"],
    "discount_total": 1000 + 100 + 2000 * 0.9,  # A:1000 不>500？1000>500 打9折... 等等 A 也是 >500
    "avg": (1000 + 2000) / 2,
}
# A 的 amount=1000 > 500 → 1000*0.9；B=100 → 100；C=2000>500 → 2000*0.9
expect1["discount_total"] = 1000 * 0.9 + 100 + 2000 * 0.9
run_case("三订单 [A:1000,B:100,C:2000]", orders1, vip_levels=["vip"], expect=expect1)

print("\n===== 最高金额买家不是第一个订单（top_buyer 恒等 bug 验证） =====")
# 期望 top_buyer=C（最高 3000），实际 top_name 初始为 A，且 amount>best 恒 False → 保持 A
orders2 = [
    {"name": "A", "amount": 50, "level": "normal"},
    {"name": "B", "amount": 1000, "level": "normal"},
    {"name": "C", "amount": 3000, "level": "vip"},
]
out2 = run_case("三订单 [A:50,B:1000,C:3000]", orders2, vip_levels=["vip"], expect={
    "total": 4050,
    "count": 3,
    "vip_total": 3000,
    "top_buyer": "C",
    "flagged": ["C"],
    "discount_total": 50 + 1000 + 3000 * 0.9,
    "avg": (1000 + 3000) / 2,
})

print("\n===== SQL 注入风险验证 =====")
evil = [{"name": "O'Brien", "amount": 10, "level": "normal"}]
run_case("买家名含单引号 O'Brien", evil, vip_levels=[], expect={
    "total": 10, "count": 1, "vip_total": 0, "top_buyer": "O'Brien",
    "flagged": [], "discount_total": 10, "avg": 10.0,
})

print("\n===== 可变默认参数共享验证 =====")
# vip_levels=[] 默认对象共享（演示反模式风险）
f = summarize_orders
print(f"默认 vip_levels 对象 id: {id(f.__defaults__[1])}")
