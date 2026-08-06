qmSTATUS: SUCCESS
SUMMARY: 已依据 reviewer 审查结论完成 rank_students 修复：遍历全部学生收集分数（修复漏掉第一个学生）、空列表安全返回约定空结果（不崩溃）、runner_up 基于唯一分数集合取第二高不同分数（消除 None 比较 TypeError，并列语义在 docstring 明确）、students=None 哨兵（消除可变默认参数反模式）、直接 return result（去掉冗余 ranked）。实测覆盖正常多学生/两元素/单元素/空列表/并列最高/全相同/顺序随机/无参调用等场景全部通过，doctest 亦通过。修复代码见 workspace/fixed_rank_students.py，验证脚本见 workspace/verify_fixed_rank_students.py。

DELIVERABLES:
- shared/tasks/rank-students-review-20260805-050346-02/workspace/fixed_rank_students.py
- shared/tasks/rank-students-review-20260805-050346-02/workspace/verify_fixed_rank_students.py

NOTES:
- HIGH-1（range(1,...) 漏掉第一个学生）：改为直接遍历全部学生收集 scores = [s["score"] for s in students]，top/passed/avg/names 均基于完整数据。实测 [A:100,B:50] → top=100、avg=75.0（原实现 top=50、avg=50.0）。
- HIGH-2（空/单元素崩溃）：入口守卫 if not students 返回约定空结果 {"top": None, "runner_up": None, "passed": 0, "avg": 0.0, "names": []}；单元素列表正常计算（top=该分数、runner_up=None、avg=该分数）。实测空列表不再抛 IndexError/ZeroDivisionError。
- HIGH-3（second=None 与 int 比较 TypeError）：runner_up 改为对唯一分数集合排序取第二高不同分数（sorted(set(scores))[-2]），无 None 比较。实测 [A:100,B:50,C:80] → runner_up=80，不再崩溃。
- MEDIUM-1（可变默认参数）：签名改为 students=None 哨兵 + 内部判空，消除跨调用状态污染与无参调用崩溃。实测连续两次无参调用结果一致且互不影响。
- MEDIUM-2（并列语义）：docstring 明确契约 runner_up 为第二高的不同分数；不足两个不同分数（空列表、单元素、全并列最高）时为 None。实测 [A:90,B:90,C:80] → runner_up=80（第二不同分数）、[A:90,B:90,C:90] → runner_up=None。
- LOW-1（avg 基于不完整 scores）：随 HIGH-1 修复，avg 基于完整 scores。
- LOW-2（ranked 冗余）：去掉 ranked 列表，直接 return result，names/scores 用列表推导简化。
- LOW-3（缺 docstring/KeyError 风险）：补充 docstring 明确输入结构（元素须含 name/score 键）、空列表行为、并列 runner_up 契约，并附 doctest 示例（实测通过）。
