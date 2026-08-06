"""验证脚本：对原始 process_comments 进行边界/逻辑/安全验证（覆盖 spec 要求场景）。"""


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


def run_case(name, comments, blocked_words=None, highlight=None):
    try:
        out = process_comments(list(comments), blocked_words if blocked_words is not None else [], highlight)
        print(f"{name:<52} -> OK  {out}")
    except Exception as e:
        print(f"{name:<52} -> EXCEPTION {type(e).__name__}: {e}")


print("===== 边界/崩溃场景 =====")
run_case("空列表 []", [])
run_case("单元素 [A:'hi']", [{"name": "A", "text": "hi"}])

print("\n===== 正常多元素（验证漏第一个评论） =====")
run_case("两评论 [A:'first', B:'second']", [
    {"name": "A", "text": "first"},
    {"name": "B", "text": "second"},
])

print("\n===== 别名副作用验证 =====")
orig = [{"name": "A", "text": "hi"}, {"name": "B", "text": "hello @bob"}]
try:
    process_comments(orig)
    print(f"调用后调用方 comments: {orig}  ← 被追加 SYS 评论（调用方数据被修改）")
except Exception as e:
    print(f"调用抛 {type(e).__name__}: {e}")
    print(f"调用后调用方 comments: {orig}")

print("\n===== mention 提取场景 =====")
run_case("text 末尾含 @", [
    {"name": "A", "text": "hi"},
    {"name": "B", "text": "hello @"},
])
run_case("含多个 @", [
    {"name": "A", "text": "hi"},
    {"name": "B", "text": "@alice hi @bob"},
])
run_case("@ 后直接接词无空格", [
    {"name": "A", "text": "hi"},
    {"name": "B", "text": "a@b@c"},
])

print("\n===== HTML 特殊字符（XSS/HTML 破坏） =====")
run_case("text 含 <script>", [
    {"name": "A", "text": "hi"},
    {"name": "B", "text": "<script>alert(1)</script>"},
])
run_case("name 含 <b>", [
    {"name": "A", "text": "hi"},
    {"name": "B", "text": "x"},
])

print("\n===== blocked_words 命中（重复问题） =====")
run_case("同评论命中两个词", [
    {"name": "A", "text": "hi"},
    {"name": "B", "text": "bad word here"},
], blocked_words=["bad", "word"])
run_case("同作者两条评论命中", [
    {"name": "A", "text": "hi"},
    {"name": "B", "text": "bad one"},
    {"name": "B", "text": "bad two"},
], blocked_words=["bad"])

print("\n===== highlight 命中 =====")
run_case("highlight='bad'", [
    {"name": "A", "text": "hi"},
    {"name": "B", "text": "this is bad word"},
], highlight="bad")

print("\n===== 可变默认参数共享验证 =====")
print(f"blocked_words 默认对象 id: {id(process_comments.__defaults__[0])}")
