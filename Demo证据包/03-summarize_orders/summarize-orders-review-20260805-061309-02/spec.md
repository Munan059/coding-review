# 任务：修复 summarize_orders 函数

## 背景

reviewer 已审查 summarize_orders（任务 -01），确认 4 个高严重度缺陷（含安全风险）：
- HIGH-1：`range(1, len(orders))` 漏掉第一个订单，avg 错误（[A:1000,B:100,C:2000] 期望 avg=1500 实际 1050）；
- HIGH-2：空/单元素列表 `orders[0]` 抛 IndexError、len=0 抛 ZeroDivisionError；
- HIGH-3：top_buyer 恒等于第一个买家名（amount>best 恒 False，[A:50,B:1000,C:3000] 期望 C 实际 A）；
- HIGH-4：SQL 字符串拼接注入（买家名 x' OR '1'='1 直接进 SQL）。
- MEDIUM：可变默认参数 vip_levels=[]；统计函数内嵌 send_alert 副作用；外部依赖 db 未定义。
- LOW：avg 衍生、KeyError 风险、缺 docstring、result 冗余、浮点精度。

原始代码位于 `shared/tasks/summarize-orders-review-20260805-061309-01/workspace/original_summarize_orders.py`，审查报告见 `shared/tasks/summarize-orders-review-20260805-061309-01/workspace/review_report.md`。

## 预期结果

1. 生成修复后的 `summarize_orders` 实现，写入 `shared/tasks/summarize-orders-review-20260805-061309-02/workspace/fixed_summarize_orders.py`，修复上述 HIGH/MEDIUM/LOW 问题：遍历全部订单、入口守卫（空列表安全）、top_buyer 用 max 按金额取买家、SQL 改为参数化查询、vip_levels 用 None 哨兵、统计与 send_alert 解耦（可注入或移除）、db 依赖注入、补 docstring。保持函数对外契约清晰（docstring 写明返回值结构与各字段语义）。
2. 编写验证脚本 `workspace/verify_fixed_summarize_orders.py` 并实测通过（覆盖：正常多订单、单元素、空列表、top_buyer 归属、SQL 注入防护、无参调用等）。
3. 发布 `shared/tasks/summarize-orders-review-20260805-061309-02/result.md`，含 STATUS、SUMMARY、DELIVERABLES 及逐项 NOTES（说明 HIGH-1/HIGH-2/HIGH-3/HIGH-4/MEDIUM/LOW 的处理方式）。
4. 按共享状态板协议，将 fixed_code 摘要回填到 `shared/state-board/summarize-orders-review-20260805-061309.json`（仅更新自己负责字段后推送）。
5. 完成后在当前房间 @mention @orchestrator:matrix-local.agentteams.io:18080 报告结果。