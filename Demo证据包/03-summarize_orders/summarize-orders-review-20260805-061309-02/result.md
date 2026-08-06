STATUS: SUCCESS
SUMMARY: 已依据 reviewer 审查结论完成 summarize_orders 修复：遍历全部订单收集金额（修复漏首单致 avg 错误）、空列表入口守卫返回约定空结果（不再 IndexError/ZeroDivisionError）、top_buyer 用 max 按金额取买家（修复恒等于首买家）、SQL 改为参数化查询（占位符+参数分离，修复注入）、vip_levels 用 None 哨兵（消除可变默认参数）、统计与 send_alert 解耦（仅返回 flagged，移除内嵌副作用）、execute_query 依赖注入（默认 None 不执行查询）、补 docstring 契约、去 result 冗余初始化、Decimal 计算折扣规避浮点精度。实测 7 项验证全部通过（正常多订单/单元素/空列表/top_buyer 归属/SQL 注入防护/无参调用/默认参数无污染），doctest 通过。白板 fixed_code 字段已回填并推送。注：本次重新提交仅更正 HIGH-1 NOTES 中 avg 数字笔误（1500.0 → 1033.33），代码与交付物未改动。

DELIVERABLES:
- shared/tasks/summarize-orders-review-20260805-061309-02/workspace/fixed_summarize_orders.py
- shared/tasks/summarize-orders-review-20260805-061309-02/workspace/verify_fixed_summarize_orders.py

NOTES:
- HIGH-1（range(1,...) 漏掉第一个订单致 avg 错误）：改为直接遍历全部订单收集 amounts = [order["amount"] for order in orders]，avg=total/count 基于完整数据。实测 [A:1000,B:100,C:2000] → avg=1033.33（(1000+100+2000)/3=1033.33，原实现漏首单得 1050.0）。
- HIGH-2（空/单元素崩溃）：入口守卫 if not orders 返回约定空结果（total=0/count=0/vip_total=0/top_buyer=None/flagged=[]/avg=0.0/discount_total=0）；单元素正常计算（top_buyer=该买家、avg=该金额）。实测不再抛 IndexError/ZeroDivisionError。
- HIGH-3（top_buyer 恒等于首个买家）：改为 top_buyer = max(orders, key=lambda o: o["amount"])["name"]，按金额取最大买家（并列取首个）。实测 [A:50,B:1000,C:3000] → top_buyer='C'（原实现 'A'）。
- HIGH-4（SQL 注入）：改为参数化查询 execute_query("SELECT * FROM orders WHERE buyer = ?", (top_buyer,))，占位符与参数分离，禁止字符串拼接。实测恶意买家名 x' OR '1'='1 作为参数传入，不进 SQL 语句。
- MEDIUM-1（可变默认参数）：vip_levels 改 None 哨兵 + 内部判空，消除跨调用共享。实测连续两次无参调用结果一致且互不影响。
- MEDIUM-2（统计内嵌 send_alert 副作用）：summarize_orders 仅返回 flagged 列表，不再在统计过程触发 send_alert，告警由调用方决定。
- MEDIUM-3（外部依赖 db 未定义）：execute_query 改为可选参数注入（默认 None 表示不执行查询），函数可独立测试，不再依赖全局 db。
- LOW-1（avg 衍生）：随 HIGH-1 修复基于完整 amounts。
- LOW-2（KeyError 风险）：docstring 明确输入契约（每个订单须含 name/amount/level 键）。
- LOW-3（缺 docstring）：补充 Args/Returns/Raises 说明，明确返回值各字段语义（total/count/vip_total/top_buyer/flagged/avg/discount_total）及空列表行为，附 doctest 示例。
- LOW-4（result 冗余初始化）：直接构造返回字典，去掉预先赋值再覆盖的冗余。
- LOW-5（浮点精度）：折扣计算用 Decimal(str(amount))*Decimal('0.9') 后 round 2 位，规避 0.9 浮点近似误差。
