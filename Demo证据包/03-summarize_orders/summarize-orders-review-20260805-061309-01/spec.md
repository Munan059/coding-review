# 审查任务：summarize_orders 函数

## 背景

用户提交了以下 Python 代码，怀疑存在 bug，请审查：

```python
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
```

函数期望输出：`{"total": 订单总额, "count": 订单数, "vip_total": VIP 订单总额, "top_buyer": 最高金额买家名, "flagged": 金额>1000 的买家名列表, "discount_total": 金额>500 打9折后的总额, "avg": 平均金额}`。

注意：代码调用了未在本文件定义的 `db`（`execute_query` 内），且 `send_alert` 有真实副作用（print）。审查时应区分「代码逻辑 bug」与「外部依赖/副作用风险」。

## 任务要求

1. 静态审查该函数：找出所有问题（bug、边界条件、可变默认参数、副作用、外部依赖、安全风险如 SQL 注入、可读性/契约问题）。
2. 对每个问题标注严重度（HIGH / MEDIUM / LOW）并说明影响：哪些输入会导致 IndexError / ZeroDivisionError / 错误结果 / 意外副作用。
3. 给出修复方向建议（不要代替 fixer 写最终代码）。
4. 可运行原始代码验证你的判断，但请保留原始代码文件作为证据；涉及 `db`/`send_alert` 的执行请用桩函数隔离。

## 预期产出

- 在 `shared/tasks/summarize-orders-review-20260805-061309-01/workspace/` 下输出审查报告 `review_report.md`。
- 按 Worker 任务参与规范发布 `shared/tasks/summarize-orders-review-20260805-061309-01/result.md`，包含 STATUS、SUMMARY、DELIVERABLES。
- 完成后在团队房间 @mention orchestrator 汇报结果。