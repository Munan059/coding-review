# 任务：测试 summarize_orders 修复结果

## 背景

reviewer 已审查 summarize_orders（任务 -01）确认缺陷，fixer 已完成修复（任务 -02），修复代码位于 `shared/tasks/summarize-orders-review-20260805-061309-02/workspace/fixed_summarize_orders.py`。本次任务由你（tester）独立验证修复后行为正确且无回归。

修复后的契约（以 fixed_summarize_orders.py docstring 为准）：
- 签名 `summarize_orders(orders, vip_levels=None, execute_query=None)`
- 返回 dict：total / count / vip_total / top_buyer / flagged / avg / discount_total
- avg = total/count（**基于全部订单**）；空列表 avg=0.0、top_buyer=None、flagged=[]、total=0
- top_buyer = 金额最高买家（并列取输入顺序第一个）；flagged = 金额 > 1000 的买家名
- discount_total：金额 > 500 打 9 折、否则原价，Decimal 计算后保留 2 位
- execute_query=None 时不执行查询；传入时按参数化方式调用 execute_query(sql, params)
- 无副作用：不内嵌 send_alert

## 预期结果

1. 读取修复代码，设计并运行覆盖以下场景的测试用例：
   - 正常多订单（如 [A:1000,B:100,C:2000] → total=3100、count=3、avg=1033.3333...、top_buyer=C）
   - 单元素、空列表、无参（vip_levels 缺省）调用（不崩溃）
   - top_buyer 归属（如 [A:50,B:1000,C:3000] → C）
   - SQL 注入防护（恶意买家名不拼进 SQL，参数化调用）
   - 默认参数无污染（连续无参调用一致）
2. 若可能，用原始（修复前）代码做对比回归，确认原 bug 可复现、修复后通过。原始代码位于 `shared/tasks/summarize-orders-review-20260805-061309-01/workspace/original_summarize_orders.py`。
3. 将测试脚本与测试报告写入 `shared/tasks/summarize-orders-review-20260805-061309-03/workspace/`，发布 `shared/tasks/summarize-orders-review-20260805-061309-03/result.md`，含 STATUS、SUMMARY、DELIVERABLES，必要时加 NOTES。
4. 按共享状态板协议，将 test_result 摘要回填到 `shared/state-board/summarize-orders-review-20260805-061309.json`（仅更新自己负责字段后推送）。
5. 完成后在当前房间 @mention @orchestrator:matrix-local.agentteams.io:18080 报告结果。