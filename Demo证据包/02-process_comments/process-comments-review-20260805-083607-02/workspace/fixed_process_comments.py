"""修复后的 process_comments 实现。

修复依据：reviewer 审查结论（process-comments-review-20260805-083607-01）
- HIGH-1：range(1,len(comments)) 漏掉第一个评论。
- HIGH-2：空列表 count=0 抛 ZeroDivisionError、comments[0] IndexError。
- HIGH-3：data=comments 别名 + append SYS 评论修改调用方输入。
- HIGH-4：name/text/highlight 未 HTML 转义直接拼接（XSS）。
- MEDIUM-1：mention 提取脆弱（@ 末尾空串、多个@只取第一个、a@b@c 错误）。
- MEDIUM-2：flagged 重复（同评论多词/同作者多评论）。
- MEDIUM-3：blocked_words=[] 可变默认参数。
- MEDIUM-4：flagged 基于替换后文本误判风险。
- LOW：缺 docstring、html 拼接低效、top 并列语义不明。
"""

import html
import re


def process_comments(comments, blocked_words=None, highlight=None):
    """处理评论列表，返回统计与 HTML 渲染结果（纯函数，无副作用）。

    Args:
        comments: 评论字典列表，每个元素形如 {"name": str, "text": str}，
            必须包含 name/text 两个键。函数不会修改调用方传入的列表。
        blocked_words: 需标记的屏蔽词列表；默认 None（等价于空列表）。
            None 哨兵避免可变默认参数反模式。
        highlight: 可选高亮词；在 HTML 输出中以 <b> 标签包裹（转义后）。

    Returns:
        结果字典，包含：
        - mentions: 全部 @用户名 列表（正则 @(\\w+) 提取，排除空串，
          支持多个 @；如 "@alice hi @bob" → ['alice','bob']）。
        - count: 评论条数；空输入时为 0。
        - html: HTML 片段（name/text/highlight 均已 html.escape 转义，
          防 XSS）；空输入时为 ""。
        - flagged: 命中 blocked_words 的评论作者名（基于原始 text 检查，
          去重、按输入顺序）；空输入时为 []。
        - avg_len: 平均文本长度 = 总长度/count；空输入时为 None。
        - top: 文本最长的评论作者名（并列取输入顺序第一个）；空输入时
          为 None。

    Examples:
        >>> process_comments([{"name": "A", "text": "hi @bob"}])["count"]
        1
        >>> process_comments([{"name": "A", "text": "<script>"}])["html"]
        '<div>A: &lt;script&gt;</div>'
    """
    # MEDIUM-3 修复：None 哨兵，避免可变默认参数反模式
    if blocked_words is None:
        blocked_words = []

    # HIGH-2 修复：空输入守卫，返回约定空结果（不崩溃）
    if not comments:
        return {
            "mentions": [],
            "count": 0,
            "html": "",
            "flagged": [],
            "avg_len": None,
            "top": None,
        }

    mentions = []
    flagged = []
    html_parts = []
    total_len = 0

    # HIGH-1 修复：遍历全部评论（含第一条），不再漏掉
    for c in comments:
        name = c["name"]
        text = c["text"]
        total_len += len(text)

        # MEDIUM-1 修复：正则提取全部 mention（排除空串、支持多个 @）
        mentions.extend(re.findall(r"@(\w+)", text))

        # MEDIUM-4 修复：flagged 基于原始 text 检查（与渲染解耦）；
        # MEDIUM-2 修复：去重（同评论多词/同作者多评论只记一次）
        for w in blocked_words:
            if w in text and name not in flagged:
                flagged.append(name)

        # HIGH-4 修复：HTML 转义 name/text/highlight（防 XSS）
        escaped_name = html.escape(name)
        escaped_text = html.escape(text)
        if highlight is not None:
            escaped_hl = html.escape(highlight)
            escaped_text = escaped_text.replace(escaped_hl, "<b>" + escaped_hl + "</b>")

        # LOW-2 修复：join 拼接替代循环 +=
        html_parts.append("<div>" + escaped_name + ": " + escaped_text + "</div>")

    count = len(comments)
    avg_len = total_len / count
    # LOW-3 修复：top 并列取输入顺序第一个（max 天然取首个并列者）
    top_comment = max(comments, key=lambda c: len(c["text"]))

    # HIGH-3 修复：移除 data=comments 别名与 append SYS 副作用（纯函数）
    return {
        "mentions": mentions,
        "count": count,
        "html": "".join(html_parts),
        "flagged": flagged,
        "avg_len": avg_len,
        "top": top_comment["name"],
    }
