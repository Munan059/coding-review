# 单独验证 scores 收集逻辑：第一个学生分数应被计入最高分
s = [{"name": "A", "score": 100}, {"name": "B", "score": 90}, {"name": "C", "score": 80}]
scores = []
for i in range(1, len(s)):
    scores.append(s[i]["score"])
print(f"students 分数: [100, 90, 80] -> scores 实际收集: {scores}  (漏掉了第一个学生 100)")
print(f"期望 top=100，但 scores[0]={scores[0]} 且 max={max(scores)}")

print("\n===== 可变默认参数共享验证 =====")
r1 = rank_students()
r2 = rank_students()
print(f"两次无参调用返回同一默认列表对象: {rank_students.__defaults__[0] is rank_students.__defaults__[0]}")
print(f"默认参数对象 id: {id(rank_students.__defaults__[0])}")
# 如果函数修改默认列表，第二次调用会受影响（演示共享风险）
