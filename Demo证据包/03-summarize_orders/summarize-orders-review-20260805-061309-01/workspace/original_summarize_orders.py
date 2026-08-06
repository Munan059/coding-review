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


def send_alert(name):
    print("alert: " + name)


def execute_query(q):
    return db.run(q)
