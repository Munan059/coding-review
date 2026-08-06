"""process_comments 修复结果独立测试脚本（tester）。

测试对象：
    shared/tasks/process-comments-review-20260805-083607-02/workspace/fixed_process_comments.py

测试目标：
    1. 契约验证（docstring）：mentions/count/html/flagged/avg_len/top
    2. 覆盖正常多评论/单元素/空列表/别名检查/XSS 转义/mention 提取/flagged 去重/top 并列
    3. 与修复前（原始实现）做对比回归：确认原 bug 可复现、修复后通过
"""

import math
import os
import sys

# 修复代码路径（fixer 交付物）
FIXED_DIR = os.path.normpath(
    os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..", "..", "process-comments-review-20260805-083607-02", "workspace",
    )
)
sys.path.insert(0, FIXED_DIR)

from fixed_process_comments import process_comments as process_comments_fixed  # noqa: E402


def C(name, text, highlight=None):
    c = {"name": name, "text": text}
    if highlight is not None:
        c["highlight"] = highlight
    return c


# ---------------------------------------------------------------------------
# 修复前（原始实现）：与 -01 审查对象一致，用于回归对比（调用时传副本防污染）。
# ---------------------------------------------------------------------------
def process_comments_original(comments, blocked_words=[], highlight=None):
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


FAILED = 0


def check_fixed(label, got, expected):
    global FAILED
    ok = got == expected
    mark = "PASS" if ok else "FAIL"
    print(f"{mark}  [{label}] 结果={got!r}")
    if not ok:
        print(f"        期望={expected!r}")
        FAILED += 1
    return ok


if __name__ == "__main__":
    print("测试对象: fixed_process_comments.py @", FIXED_DIR)

    # ============ 1) 修复后契约用例 ============
    print("\n===== 修复后：契约用例 =====")

    # 1.1 正常多评论（首条不丢、mention 多@、top 最长）
    got = process_comments_fixed([C("A", "first @alice"), C("B", "second @bob @carol")])
    check_fixed("正常多评论（首条不丢/multi-mention/top）", got,
                {"mentions": ["alice", "bob", "carol"], "count": 2,
                 "html": "<div>A: first @alice</div><div>B: second @bob @carol</div>",
                 "flagged": [], "avg_len": 15.0, "top": "B"})

    # 1.2 单元素
    got = process_comments_fixed([C("A", "hi")])
    check_fixed("单元素 [A:'hi']", got,
                {"mentions": [], "count": 1, "html": "<div>A: hi</div>",
                 "flagged": [], "avg_len": 2.0, "top": "A"})

    # 1.3 空列表
    got = process_comments_fixed([])
    check_fixed("空列表 []", got,
                {"mentions": [], "count": 0, "html": "",
                 "flagged": [], "avg_len": None, "top": None})

    # 1.4 XSS 转义（HIGH-4）：text 含 <script>，html 中应被转义
    got = process_comments_fixed([C("A", "safe"), C("E", "<script>alert(1)</script>")])
    if "<script>" not in got["html"] and "&lt;script&gt;" in got["html"]:
        print("PASS  [XSS text 转义] html 无原始 <script>，含 &lt;script&gt;")
    else:
        print(f"FAIL  [XSS text 转义] html={got['html']!r}")
        FAILED += 1

    # 1.5 XSS name 转义
    got = process_comments_fixed([C("<b>evil</b>", "x")])
    if "<b>evil</b>" not in got["html"] and "&lt;b&gt;evil&lt;/b&gt;" in got["html"]:
        print("PASS  [XSS name 转义] name 被转义")
    else:
        print(f"FAIL  [XSS name 转义] html={got['html']!r}")
        FAILED += 1

    # 1.6 mention 多场景
    got = process_comments_fixed([C("A", "@alice hi @bob"), C("B", "hi @")])
    if got["mentions"] == ["alice", "bob"]:
        print("PASS  [mention 多@/排除空串] ['alice','bob']（末尾 @ 不产生空串）")
    else:
        print(f"FAIL  [mention 多@/排除空串] {got['mentions']!r}")
        FAILED += 1
    got = process_comments_fixed([C("A", "a@b@c")])
    if got["mentions"] == ["b", "c"]:
        print("PASS  [mention a@b@c] ['b','c']")
    else:
        print(f"FAIL  [mention a@b@c] {got['mentions']!r}")
        FAILED += 1

    # 1.7 flagged 去重 + 基于原始 text
    got = process_comments_fixed([C("A", "bad worse stuff"), C("B", "bad again"), C("B", "ok")],
                                 blocked_words=["bad", "worse"])
    if got["flagged"] == ["A", "B"]:
        print("PASS  [flagged 去重] ['A','B']（同评论多词/同作者多评论均去重）")
    else:
        print(f"FAIL  [flagged 去重] {got['flagged']!r}")
        FAILED += 1
    # highlight 不干扰 flagged（基于原始 text）
    got = process_comments_fixed([C("A", "spam word")], blocked_words=["word"], highlight="spam")
    if got["flagged"] == ["A"]:
        print("PASS  [flagged 原始 text] highlight 替换不影响命中")
    else:
        print(f"FAIL  [flagged 原始 text] {got['flagged']!r}")
        FAILED += 1

    # 1.8 top 并列取首个
    got = process_comments_fixed([C("A", "aa"), C("B", "bb")])
    if got["top"] == "A":
        print("PASS  [top 并列取首个] A")
    else:
        print(f"FAIL  [top 并列取首个] {got['top']!r}")
        FAILED += 1

    # 1.9 无参调用（blocked_words 缺省）
    got = process_comments_fixed([C("A", "hi")])
    if got["flagged"] == []:
        print("PASS  [无参调用] blocked_words 缺省正常，flagged=[]")
    else:
        print(f"FAIL  [无参调用] {got['flagged']!r}")
        FAILED += 1

    # ============ 2) 别名检查（HIGH-3） ============
    print("\n===== 修复后：别名检查 =====")
    comments = [C("A", "first"), C("B", "second")]
    process_comments_fixed(comments)
    if comments == [C("A", "first"), C("B", "second")]:
        print("PASS  调用后 comments 未被修改（无别名/append SYS 副作用）")
    else:
        print(f"FAIL  调用后 comments 被修改为 {comments!r}")
        FAILED += 1

    # ============ 3) 回归对比：原始实现（预期暴露原 bug） ============
    print("\n===== 回归对比：原始实现（预期暴露原 bug） =====")
    bug_reproduced = 0

    def rep(label, desc):
        global bug_reproduced
        bug_reproduced += 1
        print(f"复现  {label} {desc}（原 bug 可复现）")

    # 3.1 漏首评论（HIGH-1）
    try:
        got = process_comments_original([C("A", "first"), C("B", "second")])
        if got["count"] == 1 and got["avg_len"] == 6.0:
            rep("[漏首评论]", f"count=1/avg_len=6.0（仅解析 B，期望 count=2/avg_len=5.5）")
    except Exception as e:
        rep("[漏首评论-异常]", f"抛 {type(e).__name__}: {e}")

    # 3.2 空输入 ZeroDivisionError（HIGH-2）
    try:
        process_comments_original([])
        rep("[空输入]", "原实现未崩溃（异常）")
    except ZeroDivisionError:
        rep("[空输入]", "原实现抛 ZeroDivisionError（count=0 除零）")

    # 3.3 单元素 ZeroDivisionError（HIGH-2）
    try:
        process_comments_original([C("A", "hi")])
        rep("[单元素]", "原实现未崩溃（异常）")
    except ZeroDivisionError:
        rep("[单元素]", "原实现抛 ZeroDivisionError（range(1,1) 空循环致 count=0）")

    # 3.4 别名副作用（HIGH-3）
    comments_b = [C("A", "first"), C("B", "second")]
    try:
        process_comments_original(comments_b)
    except Exception:
        pass
    if comments_b[-1].get("name") == "SYS":
        rep("[别名]", f"调用方 comments 被追加 SYS 评论: {comments_b!r}")
    elif len(comments_b) != 2:
        rep("[别名]", f"调用方 comments 被修改: {comments_b!r}")

    # 3.5 XSS 未转义（HIGH-4）
    try:
        got = process_comments_original([C("A", "safe"), C("E", "<script>alert(1)</script>")])
        if "<script>alert(1)</script>" in got["html"]:
            rep("[XSS]", f"html 含未转义 <script>（XSS 可注入）: {got['html']!r}")
    except Exception as e:
        rep("[XSS-异常]", f"抛 {type(e).__name__}: {e}")

    # 3.6 mention 提取脆弱（MEDIUM-1）：多@只取第一个 / 末尾@产生空串
    try:
        got = process_comments_original([C("A", "x"), C("B", "@alice hi @bob")])
        if got["mentions"] == ["alice"]:
            rep("[mention多@]", f"仅提取第一个 @alice（丢失 @bob）: {got['mentions']!r}")
    except Exception as e:
        rep("[mention多@-异常]", f"抛 {type(e).__name__}: {e}")
    try:
        got = process_comments_original([C("A", "x"), C("B", "hi @")])
        if got["mentions"] == [""]:
            rep("[mention空串]", f"末尾 @ 产生空串 mention: {got['mentions']!r}")
    except Exception as e:
        rep("[mention空串-异常]", f"抛 {type(e).__name__}: {e}")

    # 3.7 flagged 重复（MEDIUM-2）：同作者多评论含屏蔽词
    try:
        got = process_comments_original([C("A", "x"), C("B", "bad one"), C("B", "bad two")],
                                        blocked_words=["bad"])
        if got["flagged"] == ["B", "B"]:
            rep("[flagged重复]", f"同作者多评论未去重: {got['flagged']!r}")
    except Exception as e:
        rep("[flagged重复-异常]", f"抛 {type(e).__name__}: {e}")

    print(f"\n原 bug 复现次数（修复前暴露的缺陷用例数）: {bug_reproduced}")

    if FAILED:
        print(f"\n测试结果: {FAILED} 项失败 ❌")
        sys.exit(1)
    print("\n测试结果: 全部通过 ✅（修复后行为正确，无回归）")
