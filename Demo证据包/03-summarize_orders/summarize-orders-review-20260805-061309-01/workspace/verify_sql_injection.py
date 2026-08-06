"""补充验证：SQL 注入风险 + 可变默认参数共享。"""
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


print("===== SQL 注入场景（恶意买家名在第一位，因 top_name 恒等 bug 会直接进入 SQL） =====")
evil = [
    {"name": "x' OR '1'='1", "amount": 100, "level": "normal"},
    {"name": "B", "amount": 200, "level": "normal"},
]
alert_calls.clear()
sql_calls.clear()
out = summarize_orders(evil, [])
print(f"top_buyer = {out['top_buyer']!r}")
print(f"execute_query 收到的 SQL: {sql_calls[0]!r}")
print("→ 买家名直接拼入 SQL，单引号未转义，存在 SQL 注入风险（若 db 为真实数据库，' OR '1'='1 会匹配全部行）")

print("\n===== 可变默认参数共享验证 =====")
print(f"summarize_orders 默认参数个数: {len(summarize_orders.__defaults__)}")
print(f"默认 vip_levels 对象 id: {id(summarize_orders.__defaults__[0])}")
print("→ vip_levels=[] 默认列表在函数定义时创建一次，所有未显式传 vip_levels 的调用共享同一对象（反模式）")
