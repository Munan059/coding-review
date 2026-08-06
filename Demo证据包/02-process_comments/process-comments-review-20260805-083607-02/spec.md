# 任务：修复 process_comments 函数

## 背景

reviewer 已审查 process_comments（任务 -01），确认 4 个高严重度缺陷（含 XSS 安全漏洞）：
- HIGH-1：`range(1,len(comments))` 漏掉第一个评论（[A:'first',B:'second'] count=1 应 2、单元素 ZeroDivisionError）；
- HIGH-2：空列表 count=0 抛 ZeroDivisionError、comments[0] IndexError；
- HIGH-3：data=comments 别名 + append SYS 评论修改调用方输入（实测调用后被追加）；
- HIGH-4（安全）：name/text/highlight 未 HTML 转义直接拼接（text='<script>alert(1)</script>' 原样进 html → XSS）。
- MEDIUM：mention 提取脆弱（@ 末尾空串、多个@只取第一个、a@b@c 错误提取）、flagged 重复（同评论多词/同作者多评论）、blocked_words=[] 可变默认参数、flagged 基于替换后文本误判风险。
- LOW：缺 docstring、html 拼接低效、top 并列语义不明。

原始代码位于 `shared/tasks/process-comments-review-20260805-083607-01/workspace/original_process_comments.py`，审查报告见 `shared/tasks/process-comments-review-20260805-083607-01/workspace/review_report.md`。

## 预期结果

1. 生成修复后的 `process_comments` 实现，写入 `shared/tasks/process-comments-review-20260805-083607-02/workspace/fixed_process_comments.py`，修复上述 HIGH/MEDIUM/LOW 问题：遍历全部评论、空守卫、移除别名副作用（用副本或直接读输入）、**html.escape 转义** name/text/highlight、正则提取 mention（如 @(\w+)、多个@、排除末尾空串）、flagged 去重、blocked_words 用 None 哨兵、flagged 基于原始文本检查、补 docstring 明确契约（返回值结构与 top 并列语义）。
2. 编写验证脚本 `workspace/verify_fixed_process_comments.py` 并实测通过（覆盖：正常多评论、单元素、空列表、别名检查、XSS 转义、mention 提取多场景、flagged 去重、无参调用）。
3. 发布 `shared/tasks/process-comments-review-20260805-083607-02/result.md`，含 STATUS、SUMMARY、DELIVERABLES 及逐项 NOTES（说明 HIGH-1~4/MEDIUM/LOW 的处理方式）。
4. 按共享状态板协议，将 fixed_code 摘要回填到 `shared/state-board/process-comments-review-20260805-083607.json`（仅更新自己负责字段后推送）。
5. 完成后在当前房间 @mention @orchestrator:matrix-local.agentteams.io:18080 报告结果。