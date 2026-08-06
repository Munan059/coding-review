# 审查任务：process_comments 函数

## 背景

用户提交了以下 Python 代码，怀疑存在 bug，请审查：

```python
def process_comments(comments, blocked_words=[], highlight=None):
    data = comments
    result = {"mentions": [], "count": 0, "html": "", "flagged": []}
    total_len = 0
    for i in range(1, len(comments)):
        c = comments[i]
        total_len = total_len + len(c["text"])
        name = c["name"]
        text = c["text"]
        if "@" in text:
            mention = text.split("@")[1].split(" ")[0]
            result["mentions"].append(mention)
        if highlight is not None:
            text = text.replace(highlight, "<b>" + highlight + "</b>")
        result["html"] = result["html"] + "<div>" + name + ": " + text + "</div>"
        for w in blocked_words:
            if w in text:
                result["flagged"].append(name)
        result["count"] = result["count"] + 1
    avg_len = total_len / result["count"]
    top_comment = comments[0]
    for c in comments:
        if len(c["text"]) > len(top_comment["text"]):
            top_comment = c
    result["avg_len"] = avg_len
    result["top"] = top_comment["name"]
    data.append({"name": "SYS", "text": ""})
    return result
```

函数期望输出：`{"mentions": 被@用户名列表, "count": 处理评论数, "html": 渲染后的 HTML 片段, "flagged": 命中屏蔽词的评论作者列表, "avg_len": 平均评论长度, "top": 最长评论作者}`，并假设每条评论形如 `{"name": str, "text": str}`。

## 任务要求

1. 静态审查该函数：找出所有问题（bug、边界条件、可变默认参数、别名副作用、循环范围、索引越界、ZeroDivisionError、mention 提取、HTML 转义、highlight 处理、flagged 重复、契约/可读性问题）。
2. 对每个问题标注严重度（HIGH / MEDIUM / LOW）并说明影响：哪些输入会导致 ZeroDivisionError / IndexError / 调用方数据被修改 / mention 提取错误 / HTML 破坏。
3. 给出修复方向建议（不要代替 fixer 写最终代码）。
4. 可运行原始代码验证你的判断（用不同输入实测：空列表、单元素、正常多元素、text 末尾含 @、含多个 @、含 HTML 特殊字符、blocked_words 命中、highlight 命中），并保留原始代码文件作为证据。
5. 更新状态板 `shared/state-board/process-comments-review-20260805-083607.json` 的 review_report 字段。

## 预期产出

- 在 `shared/tasks/process-comments-review-20260805-083607-01/workspace/` 下输出审查报告 `review_report.md`，并保存原始代码文件（如 `original_process_comments.py`）与验证脚本（如 `verify_original_process_comments.py`）。
- 按 Worker 任务参与规范发布 `shared/tasks/process-comments-review-20260805-083607-01/result.md`，包含 STATUS、SUMMARY、DELIVERABLES。
- 完成后在团队房间 @mention orchestrator 汇报结果。