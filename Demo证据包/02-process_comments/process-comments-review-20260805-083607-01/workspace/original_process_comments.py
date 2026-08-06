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
