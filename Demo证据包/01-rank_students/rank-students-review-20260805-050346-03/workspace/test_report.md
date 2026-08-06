# 测试报告：rank_students 修复结果验证

- 任务 ID：`rank-students-review-20260805-050346-03`
- 测试人：tester
- 测试日期：2026-08-05
- 测试对象：`shared/tasks/rank-students-review-20260805-050346-02/workspace/fixed_rank_students.py`
- 测试脚本：`shared/tasks/rank-students-review-20260805-050346-03/workspace/test_rank_students.py`

## 结论

**PASS —— 修复后行为符合 docstring 契约，12/12 契约用例 + 默认参数无污染检查全部通过，无回归。**

| 项目 | 结果 |
|---|---|
| 契约用例（正常多学生/runner_up/空/单元素/无参/并列/60 分边界）| 12 / 12 ✅ |
| 默认参数无污染（两次无参调用）| ✅ |
| 原实现缺陷复现数 | 11（9 崩溃 + 2 错误结果）|
| 退出码 | 0（全部通过）|

---

## 1. 契约用例（修复后实测）

修复后契约（docstring）：`top` 最高分（空为 None）；`runner_up` 第二高【不同】分数（不足两个不同分数为 None）；`passed` 分数 ≥ 60 人数；`avg` 平均分（空为 0.0）；`names` 按输入顺序全部姓名。

| # | 场景 | 输入 | 期望 | 修复后实际 | 结果 |
|---|---|---|---|---|---|
| 1 | 正常多学生 | `[A:100,B:50]` | top=100, runner_up=50, passed=1, avg=75.0, names=[A,B] | 同期望 | ✅ |
| 2 | 三名不同分数 | `[A:100,B:50,C:80]` | top=100, runner_up=80, passed=2, avg=76.67, names=[A,B,C] | 同期望 | ✅ |
| 3 | 单元素列表 | `[A:90]` | top=90, runner_up=None, passed=1, avg=90.0 | 同期望 | ✅ |
| 4 | 空列表 | `[]` | top=None, runner_up=None, passed=0, avg=0.0, names=[] | 同期望 | ✅ |
| 5 | 无参调用 | `rank_students()` | 同空列表 | 同期望 | ✅ |
| 6 | 显式 None | `rank_students(None)` | 同空列表 | 同期望 | ✅ |
| 7 | 并列最高 | `[A:90,B:90,C:80]` | top=90, runner_up=80（第二不同分数）| 同期望 | ✅ |
| 8 | 全并列 | `[A:85,B:85]` | top=85, runner_up=None | 同期望 | ✅ |
| 9 | 60 分边界 | `[A:60,B:59]` | top=60, runner_up=59, passed=1, avg=59.5 | 同期望 | ✅ |
| 10 | 60 分算通过 | `[A:60]` | passed=1 | 同期望 | ✅ |
| 11 | 59 分不算通过 | `[A:59]` | passed=0 | 同期望 | ✅ |
| 12 | 多学生乱序 | `[A:70,B:95,C:88,D:60]` | top=95, runner_up=88, passed=4, avg=78.25 | 同期望 | ✅ |

## 2. 默认参数无污染（MEDIUM-1）

连续两次 `rank_students()`（无参）结果一致且均为空结果 `{'top': None, 'runner_up': None, 'passed': 0, 'avg': 0.0, 'names': []}` ✅ —— `students=None` 哨兵生效，无可变默认参数状态污染。

## 3. 回归对比（修复前 / 修复后）

使用与 -01 审查对象一致的原始实现（`range(1, len(students))` + `second=None` 版本）跑同一组输入：

| 场景 | 原实现表现 | 修复后 | 结论 |
|---|---|---|---|
| `[A:100,B:50]` | top=50、runner_up=None、avg=50.0（漏首学生）| top=100、runner_up=50、avg=75.0 | HIGH-1 复现 ✅ → 已修复 ✅ |
| `[A:100,B:50,C:80]` | TypeError（second=None 与 int 比较）| runner_up=80 | HIGH-3 复现 ✅ → 已修复 ✅ |
| `[A:90]` / `[]` / `()` / `(None)` | IndexError（scores[0] 越界）| 安全返回约定结果 | HIGH-2 复现 ✅ → 已修复 ✅ |
| `[A:90,B:90,C:80]` | TypeError（second=None 比较）| runner_up=80 | HIGH-3 复现 ✅ → 已修复 ✅ |
| `[A:60,B:59]` | top=59、runner_up=None、avg=59.0（漏首学生）| top=60、runner_up=59、avg=59.5 | HIGH-1 复现 ✅ → 已修复 ✅ |
| `[A:60]` / `[A:59]` | IndexError（scores 为空）| 正常计算 | HIGH-2 复现 ✅ → 已修复 ✅ |
| `[A:70,B:95,C:88,D:60]` | TypeError（second=None 比较）| 正常计算 | HIGH-3 复现 ✅ → 已修复 ✅ |
| `[A:85,B:85]` | 恰好正确（巧合）| 正确 | 原本正确，无回归 ✅ |

**回归判定**：修复后除「原本正确」场景外，原 11 处缺陷场景（9 崩溃 + 2 错误结果）全部修复；唯一原本正确的全并列用例输出与修复后一致。**无回归**。

## 4. 修复有效性核对（对照 -01 审查结论）

| 审查项 | 修复方式（-02） | 测试验证 |
|---|---|---|
| HIGH-1 漏掉第一个学生 | 遍历全部学生收集 scores/names | ✅ 用例 1、9 通过 |
| HIGH-2 空/单元素崩溃 | 空列表守卫 + 单元素正常计算 | ✅ 用例 3、4、5、6、10、11 通过 |
| HIGH-3 runner_up TypeError | `sorted(set(scores))` 取第二高不同分数，无 None 比较 | ✅ 用例 2、7 通过 |
| MEDIUM-1 可变默认参数 | `students=None` 哨兵 | ✅ 无污染检查通过 |
| MEDIUM-2 并列语义 | 契约明确：第二高不同分数，不足两个不同分数为 None | ✅ 用例 7、8 通过 |
| LOW avg/冗余/docstring | avg 基于完整 scores、去掉 ranked、补 docstring | ✅ 代码核对 + 用例通过 |

## 5. 执行命令

```bash
$ python3 shared/tasks/rank-students-review-20260805-050346-03/workspace/test_rank_students.py
# 12/12 契约用例 + 默认参数无污染 PASS，回归对比 11 处原缺陷全部复现；EXIT=0
```

## 6. 备注（NOTES）

- 测试脚本通过相对路径动态加载 -02 的 `fixed_rank_students.py`，保证测试对象为 fixer 实际交付物。
- 未直接 import -01 原始文件（其无模块级断言，但为隔离副作用仍内联还原），原始实现与审查对象逐字一致（仅补充 `students=None` 兜底以便无参调用回归演示）。
- avg 期望值按 `230/3`、`260/3` 等精确表达式写入，与修复实现 `sum/len` 的浮点结果一致，避免近似比较误报。
- 60 分边界单独成用例：`60` 计 passed，`59` 不计，边界契约验证到位。
