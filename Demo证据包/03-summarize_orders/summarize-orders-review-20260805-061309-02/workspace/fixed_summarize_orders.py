"""修复后的 summarize_orders 实现。

修复依据：reviewer 审查结论（summarize-orders-review-20260805-061309-01）
- HIGH-1：原实现 range(1, len(orders)) 漏掉第一个订单，avg 错误。
- HIGH-2：原实现空/单元素列表 amounts[0] 抛 IndexError、len=0 抛 ZeroDivisionError。
- HIGH-3：原实现 top_buyer 恒等于第一个买家名（amount > best 恒 False）。
- HIGH-4：原实现 SQL 字符串拼接注入。
- MEDIUM-1：可变默认参数 vip_levels=[] 反模式。
- MEDIUM-2：统计函数内嵌 send_alert 副作用。
- MEDIUM-3：外部依赖 db 未定义。
- LOW：avg 衍生、KeyError 风险、缺 docstring、result 冗余、浮点精度。
"""


def summarize_orders(orders, vip_levels=None, execute_query=None):
    """汇总订单统计信息，返回结果字典（纯统计，无副作用）。

    Args:
        orders: 订单字典列表，每个元素形如 {"name": str, "amount": 数值,
            "level": str}，必须包含 name/amount/level 三个键。
        vip_levels: VIP 等级集合/列表；默认 None（等价于空集合，即无 VIP
            订单）。None 哨兵避免可变默认参数反模式。
        execute_query: 可选的 SQL 查询执行器，签名为
            execute_query(sql, params)；默认 None 表示不执行查询（纯统计）。
            查询必须使用参数化方式，禁止字符串拼接。

    Returns:
        结果字典，包含：
        - total: 全部订单金额总和；空列表时为 0。
        - count: 订单数量；空列表时为 0。
        - vip_total: level 在 vip_levels 中的订单金额总和；空列表时为 0。
        - top_buyer: 金额最高的买家名（并列时取输入顺序第一个）；空列表
          时为 None。
        - flagged: 金额 > 1000 的买家名列表（按输入顺序）；空列表时为 []。
        - avg: 平均金额（total/count）；空列表时为 0.0。
        - discount_total: 金额 > 500 打 9 折、否则原价后的累计；空列表时
          为 0。金额用 Decimal 计算后转 float，保留 2 位小数，规避浮点精度。

    Examples:
        >>> summarize_orders([{"name": "A", "amount": 1000, "level": "gold"}, {"name": "B", "amount": 100, "level": "normal"}])
        {'total': 1100, 'count': 2, 'vip_total': 0, 'top_buyer': 'A', 'flagged': [], 'avg': 550.0, 'discount_total': 1000.0}
    """
    # MEDIUM-1 修复：None 哨兵，避免可变默认参数反模式
    if vip_levels is None:
        vip_levels = []

    # HIGH-2 修复：空列表安全处理，返回约定空结果（不崩溃）
    if not orders:
        return {
            "total": 0,
            "count": 0,
            "vip_total": 0,
            "top_buyer": None,
            "flagged": [],
            "avg": 0.0,
            "discount_total": 0,
        }

    # HIGH-1 修复：遍历全部订单，不再漏掉第一个
    amounts = [order["amount"] for order in orders]

    total = sum(amounts)
    count = len(orders)
    vip_total = sum(order["amount"] for order in orders if order["level"] in vip_levels)

    # HIGH-3 修复：按金额取最大买家（max 取首个并列者），不再依赖恒假条件
    top_buyer = max(orders, key=lambda order: order["amount"])["name"]

    flagged = [order["name"] for order in orders if order["amount"] > 1000]

    avg = total / count

    # LOW-5 修复：Decimal 计算折扣，规避 0.9 浮点近似误差，保留 2 位小数
    from decimal import Decimal

    discount_total = sum(
        Decimal(str(order["amount"])) * Decimal("0.9")
        if order["amount"] > 500
        else Decimal(str(order["amount"]))
        for order in orders
    )
    discount_total = float(round(discount_total, 2))

    # HIGH-4 修复：参数化查询（占位符 + 参数分离），禁止字符串拼接
    if execute_query is not None:
        execute_query("SELECT * FROM orders WHERE buyer = ?", (top_buyer,))

    # LOW-4 修复：直接构造 result，去掉冗余初始化
    return {
        "total": total,
        "count": count,
        "vip_total": vip_total,
        "top_buyer": top_buyer,
        "flagged": flagged,
        "avg": avg,
        "discount_total": discount_total,
    }
