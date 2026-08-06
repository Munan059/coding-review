STATUS: SUCCESS
SUMMARY: 审查完成：summarize_orders 存在 4 个高严重度缺陷（含安全风险）。HIGH-1：第 5 行 range(1, len(orders)) 漏掉第一个订单，avg 错误（[A:1000,B:100,C:2000] 期望 avg=1500 实际 1050）；HIGH-2：空/单元素列表抛 IndexError、len=0 抛 ZeroDivisionError；HIGH-3：top_buyer 恒等于第一个买家名（amount>best 恒 False，[A:50,B:1000,C:3000] 期望 C 实际 A）；HIGH-4：SQL 字符串拼接注入（买家名 x' OR '1'='1 直接进 SQL）。MEDIUM：可变默认参数 vip_levels=[]；统计函数内嵌 send_alert 副作用；外部依赖 db 未定义。LOW：avg 衍生、KeyError 风险、缺 docstring、result 冗余、浮点精度。修复方向：遍历全部订单、入口守卫、max 取买家、参数化查询、None 哨兵、统计/告警分离、依赖注入。原始代码与验证脚本保留在 workspace。

DELIVERABLES:
- shared/tasks/summarize-orders-review-20260805-061309-01/workspace/review_report.md
- shared/tasks/summarize-orders-review-20260805-061309-01/workspace/original_summarize_orders.py
- shared/tasks/summarize-orders-review-20260805-061309-01/workspace/verify_original.py
- shared/tasks/summarize-orders-review-20260805-061309-01/workspace/verify_sql_injection.py
