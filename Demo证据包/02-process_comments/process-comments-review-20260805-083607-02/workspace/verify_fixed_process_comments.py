"""验证修复后的 process_comments 行为（覆盖正常/单元素/空/别名/XSS/mention/flagged/无参等）。"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fixed_process_comments import process_comments


def close(a, b, eps=1e-9):
    return abs(a - b) < eps


def check(desc, got, expected):
    ok = (
        got["mentions"] == expected["mentions"]
        and got["count"] == expected["count"]
        and got["html"] == expected["html"]
        and got["flagged"] == expected["flagged"]
        and (
            got["avg_len"] is None
            if expected["avg_len"] is None
            else close(got["avg_len"], expected["avg_len"])
        )
        and got["top"] == expected["top"]
    )
    print(f"{'PASS' if ok else 'FAIL'}  {desc}: {got}")
    return ok


failed = 0

# 1. 正常多评论（HIGH-1 场景：首条评论不丢失）
ok = check(
    "正常多评论 [A:'first', B:'second']",
    process_comments([{"name": "A", "text": "first"}, {"name": "B", "text": "second"}]),
    {
        "mentions": [],
        "count": 2,
        "html": "<div>A: first</div><div>B: second</div>",
        "flagged": [],
        "avg_len": 5.5,
        "top": "B",
    },
)
failed += 0 if ok else 1

# 2. 单元素（HIGH-2 场景：原实现 ZeroDivisionError）
ok = check(
    "单元素 [A:'hi']",
    process_comments([{"name": "A", "text": "hi"}]),
    {
        "mentions": [],
        "count": 1,
        "html": "<div>A: hi</div>",
        "flagged": [],
        "avg_len": 2.0,
        "top": "A",
    },
)
failed += 0 if ok else 1

# 3. 空列表（HIGH-2 场景：原实现 ZeroDivisionError/IndexError）
ok = check(
    "空列表 []",
    process_comments([]),
    {"mentions": [], "count": 0, "html": "", "flagged": [], "avg_len": None, "top": None},
)
failed += 0 if ok else 1

# 4. 别名检查（HIGH-3 场景：调用方输入不被修改）
comments = [{"name": "A", "text": "first"}, {"name": "B", "text": "second"}]
process_comments(comments)
if comments == [{"name": "A", "text": "first"}, {"name": "B", "text": "second"}]:
    print("PASS  输入不被修改: comments 未被追加 SYS 评论")
else:
    print(f"FAIL  输入被修改: {comments}")
    failed += 1

# 5. XSS 转义（HIGH-4 场景：text 中的脚本标签被转义）
ok = check(
    "XSS 转义 [text=<script>alert(1)</script>]",
    process_comments([{"name": "A", "text": "<script>alert(1)</script>"}]),
    {
        "mentions": [],
        "count": 1,
        "html": "<div>A: &lt;script&gt;alert(1)&lt;/script&gt;</div>",
        "flagged": [],
        "avg_len": 25.0,
        "top": "A",
    },
)
failed += 0 if ok else 1

# 6. name 也转义
ok = check(
    "name 转义 [name=<b>X</b>]",
    process_comments([{"name": "<b>X</b>", "text": "hi"}]),
    {
        "mentions": [],
        "count": 1,
        "html": "<div>&lt;b&gt;X&lt;/b&gt;: hi</div>",
        "flagged": [],
        "avg_len": 2.0,
        "top": "<b>X</b>",
    },
)
failed += 0 if ok else 1

# 7. highlight 转义 + 高亮（HIGH-4 场景：highlight 内容转义后包裹）
ok = check(
    "highlight 转义 [text='say bad', highlight='bad']",
    process_comments([{"name": "A", "text": "say bad"}], highlight="bad"),
    {
        "mentions": [],
        "count": 1,
        "html": "<div>A: say <b>bad</b></div>",
        "flagged": [],
        "avg_len": 7.0,
        "top": "A",
    },
)
failed += 0 if ok else 1

# 8. mention 多场景（MEDIUM-1 场景）
ok = check(
    "mention 多个 [@alice hi @bob]",
    process_comments([{"name": "A", "text": "@alice hi @bob"}]),
    {
        "mentions": ["alice", "bob"],
        "count": 1,
        "html": "<div>A: @alice hi @bob</div>",
        "flagged": [],
        "avg_len": 14.0,
        "top": "A",
    },
)
failed += 0 if ok else 1

ok = check(
    "mention @ 末尾 [hello @]",
    process_comments([{"name": "A", "text": "hello @"}]),
    {
        "mentions": [],
        "count": 1,
        "html": "<div>A: hello @</div>",
        "flagged": [],
        "avg_len": 7.0,
        "top": "A",
    },
)
failed += 0 if ok else 1

ok = check(
    "mention a@b@c [a@b@c]",
    process_comments([{"name": "A", "text": "a@b@c"}]),
    {
        "mentions": ["b", "c"],
        "count": 1,
        "html": "<div>A: a@b@c</div>",
        "flagged": [],
        "avg_len": 5.0,
        "top": "A",
    },
)
failed += 0 if ok else 1

# 9. flagged 去重（MEDIUM-2 场景：同评论多词/同作者多评论只记一次）
ok = check(
    "flagged 去重 [bad+word 同评论]",
    process_comments([{"name": "B", "text": "bad word"}], blocked_words=["bad", "word"]),
    {
        "mentions": [],
        "count": 1,
        "html": "<div>B: bad word</div>",
        "flagged": ["B"],
        "avg_len": 8.0,
        "top": "B",
    },
)
failed += 0 if ok else 1

ok = check(
    "flagged 同作者多评论",
    process_comments(
        [{"name": "B", "text": "bad one"}, {"name": "B", "text": "another bad"}],
        blocked_words=["bad"],
    ),
    {
        "mentions": [],
        "count": 2,
        "html": "<div>B: bad one</div><div>B: another bad</div>",
        "flagged": ["B"],
        "avg_len": 9.0,
        "top": "B",
    },
)
failed += 0 if ok else 1

# 10. flagged 基于原始 text（MEDIUM-4 场景：highlight 不影响判定）
ok = check(
    "flagged 基于原始 text [highlight='bad' + blocked='bad']",
    process_comments([{"name": "A", "text": "say bad"}], blocked_words=["bad"], highlight="bad"),
    {
        "mentions": [],
        "count": 1,
        "html": "<div>A: say <b>bad</b></div>",
        "flagged": ["A"],
        "avg_len": 7.0,
        "top": "A",
    },
)
failed += 0 if ok else 1

# 11. 无参调用（MEDIUM-3 场景：blocked_words 默认 None）
ok = check(
    "无参 blocked_words",
    process_comments([{"name": "A", "text": "hello"}]),
    {
        "mentions": [],
        "count": 1,
        "html": "<div>A: hello</div>",
        "flagged": [],
        "avg_len": 5.0,
        "top": "A",
    },
)
failed += 0 if ok else 1

# 12. top 并列取首个（LOW-3 场景）
ok = check(
    "top 并列取首个 [A:'xx', B:'yy']",
    process_comments([{"name": "A", "text": "xx"}, {"name": "B", "text": "yy"}]),
    {
        "mentions": [],
        "count": 2,
        "html": "<div>A: xx</div><div>B: yy</div>",
        "flagged": [],
        "avg_len": 2.0,
        "top": "A",
    },
)
failed += 0 if ok else 1

if failed:
    print(f"\n{failed} 项验证失败")
    sys.exit(1)
print("\n全部验证通过")
