# 代码审查报告：summarize_orders

- 任务 ID：`summarize-orders-review-20260805-061309-01`
- 审查人：reviewer
- 审查日期：2026-08-05
- 审查对象：

```python
def summarize_orders(orders, vip_levels=[]):
    result = {"total": 0, "count": 0, "vip_total": 0, "top_buyer": None, "flagged": [], "avg": 0}
    amounts = []
    for i in range(1, len(orders)):
        order = orders[i]
        amounts.append(order["amount"])
    best = amounts[0]
    for a in amounts:
        if a > best:
            best = a
    vip_sum = 0
    for order in orders:
        if order["level"] in vip_levels:
            vip_sum = vip_sum + order["amount"]
    top_name = orders[0]["name"]
    for order in orders:
        if order["amount"] > best:
            top_name = order["name"]
    discount_total = 0
    for order in orders:
        if order["amount"] > 500:
            discount_total = discount_total + order["amount"] * 0.9
        else:
            discount_total = discount_total + order["amount"]
    flagged = []
    for order in orders:
        if order["amount"] > 1000:
            flagged.append(order["name"])
            send_alert(order["name"])
    total = 0
    for order in orders:
        total = total + order["amount"]
    result["total"] = total
    result["count"] = len(orders)
    result["vip_total"] = vip_sum
    result["top_buyer"] = top_name
    result["flagged"] = flagged
    result["discount_total"] = discount_total
    result["avg"] = sum(amounts) / len(amounts)
    query = "SELECT * FROM orders WHERE buyer = '" + top_name + "'"
    execute_query(query)
    return result
```

## 结论总览

| 严重级别 | 数量 | 摘要 |
|---|---|---|
| HIGH | 4 | 漏掉第一个订单（avg 错误）；空/单元素列表崩溃；top_buyer 恒等于第一个买家名；SQL 注入 |
| MEDIUM | 3 | 可变默认参数 `vip_levels=[]`；统计函数内嵌 `send_alert` 副作用；外部依赖 `db` 未定义 |
| LOW | 5 | avg 基于不完整 amounts（衍生）；KeyError 风险；缺 docstring/契约；result 冗余初始化；浮点精度 |

**判定：存在功能性缺陷 + 安全风险，需修复后进入测试环节。**

---

## 实测验证（原始代码运行结果，db/send_alert 已打桩隔离）

| 输入 | 实际输出 | 期望输出 | 结果 |
|---|---|---|---|
| `[]`（空列表） | `IndexError: list index out of range` | 明确契约 | ✗ 崩溃 |
| `[A:100]`（单元素） | `IndexError: list index out of range` | top_buyer=A | ✗ 崩溃 |
| `[A:1000,B:100,C:2000]` | `{top_buyer:'A', avg:1050.0}` | top_buyer='C', avg=1500.0 | ✗ 错误结果 |
| `[A:50,B:1000,C:3000]` | `{top_buyer:'A', avg:2000.0}` | top_buyer='C' | ✗ 错误结果 |
| 恶意买家名 `x' OR '1'='1` | SQL=`SELECT * FROM orders WHERE buyer = 'x' OR '1'='1'` | 应参数化 | ✗ SQL 注入 |

---

## 发现明细

### [HIGH-1] 循环从索引 1 开始，漏掉第一个订单（功能性缺陷）

- **位置**：第 5 行 `for i in range(1, len(orders))`
- **问题描述**：`range` 从 `1` 开始，`orders[0]["amount"]` 不会进入 `amounts`。`best`、`avg` 均基于不完整的 `amounts` 计算。
- **实测**：`[A:1000,B:100,C:2000]` 期望 `avg=1500.0`，实际 `avg=1050.0`（只算了 B、C）。
- **影响**：`avg` 恒为「去掉第一个订单后的平均值」，统计结果错误。

### [HIGH-2] 空列表 / 单元素列表崩溃

- **位置**：第 9 行 `best = amounts[0]`；第 16 行 `top_name = orders[0]["name"]`；第 36 行 `sum(amounts) / len(amounts)`
- **问题描述**：
  - 空列表 `[]`：`amounts[0]` 抛 `IndexError`（`orders[0]["name"]` 同样崩溃；即使跳过，`len(amounts)=0` 时除法抛 `ZeroDivisionError`）；
  - 单元素列表：`range(1, 1)` 为空 → `amounts=[]` → `amounts[0]` 抛 `IndexError`。
- **实测**：`[]` 与 `[A:100]` 均抛 `IndexError: list index out of range`。
- **影响**：无法处理 0-1 个订单的输入，缺少边界守卫。

### [HIGH-3] `top_buyer` 恒等于第一个买家名（独立逻辑缺陷）

- **位置**：第 16-18 行
- **问题描述**：`top_name` 初始化为 `orders[0]["name"]`，随后用 `order["amount"] > best` 寻找更高金额的买家。但 `best` 是所有 `amounts` 的**最大值**，因此 `amount > best` 恒为 False，循环体永不执行——`top_name` **永远等于第一个订单的买家名**，与「最高金额买家」无关。
- **实测**：`[A:50,B:1000,C:3000]` 期望 `top_buyer='C'`（最高金额 3000），实际 `top_buyer='A'`；`[A:1000,B:100,C:2000]` 期望 `'C'`，实际 `'A'`。
- **影响**：即使修复 HIGH-1（best 计算正确），该逻辑依旧错误——`top_buyer` 只在第一个订单恰好是最高金额买家时才碰巧正确。核心输出字段错误。

### [HIGH-4] SQL 注入（安全缺陷）

- **位置**：第 37 行 `query = "SELECT * FROM orders WHERE buyer = '" + top_name + "'"`
- **问题描述**：买家名来自外部输入（订单数据），直接字符串拼接进 SQL，单引号未转义、未参数化。
- **实测**：买家名 `"x' OR '1'='1"` → 生成 SQL `SELECT * FROM orders WHERE buyer = 'x' OR '1'='1'`，会匹配全部订单行；恶意输入可进一步构造删除/篡改语句。
- **影响**：安全漏洞，若 `db` 为真实数据库将造成数据泄露/破坏。应改用参数化查询。

### [MEDIUM-1] 可变默认参数 `vip_levels=[]`（反模式）

- **位置**：第 1 行 `def summarize_orders(orders, vip_levels=[]):`
- **问题描述**：默认列表在函数定义时创建一次，所有未显式传 `vip_levels` 的调用共享同一对象（已实测确认共享）。当前函数只读，尚未直接污染，但一旦新增写操作即跨调用污染。
- **影响**：潜在跨调用状态污染；应改为 `vip_levels=None` 哨兵。

### [MEDIUM-2] 统计函数内嵌 `send_alert` 副作用

- **位置**：第 29 行 `send_alert(order["name"])`
- **问题描述**：`summarize_orders` 是纯统计函数，却在统计过程中执行 `send_alert`（真实副作用：print/通知）。违反单一职责：统计与告警应分离；且告警触发时机（每次统计都发）与调用方意图无关。
- **实测**：`[A:1000,B:100,C:2000]` 触发 `send_alert('C')`。
- **影响**：统计函数不可预测地产生外部副作用，测试/复用困难；若 `send_alert` 未来改为网络通知，性能与可靠性风险。

### [MEDIUM-3] 外部依赖 `db` 未定义（耦合/可测性）

- **位置**：第 40-41 行 `execute_query(q): return db.run(q)`
- **问题描述**：`db` 未在本文件定义，依赖外部全局/环境注入；`execute_query` 与 `db` 强耦合。
- **影响**：函数无法独立测试（需打桩）；若环境无 `db` 则 `NameError`。应通过依赖注入或抽象接口解耦。

### [LOW-1] `avg` 基于不完整的 `amounts`（HIGH-1 衍生）

- **位置**：第 36 行
- **问题描述**：`avg` 与 HIGH-1 同源——漏掉第一个订单的金额，且空列表时 `ZeroDivisionError`（见 HIGH-2）。
- **影响**：平均金额不准确。

### [LOW-2] KeyError 风险

- **位置**：第 6、13、16、22、27、30 行（`order["amount"]`/`order["level"]`/`order["name"]`）
- **问题描述**：输入订单字典缺任一键时抛 `KeyError`，无友好提示。
- **影响**：输入契约未明确，异常信息不友好。

### [LOW-3] 缺少 docstring 与输入契约

- **位置**：第 1 行（函数定义处）
- **问题描述**：未说明 `orders` 元素结构（name/amount/level 键）、`vip_levels` 含义、空列表行为、副作用（send_alert/execute_query）。
- **影响**：调用方无法预期边界行为与副作用。

### [LOW-4] `result` 冗余初始化

- **位置**：第 2 行
- **问题描述**：`result` 初始字典中的 `total`/`count`/`vip_total`/`top_buyer`/`avg` 随后全部被覆盖，初始值无意义；`discount_total` 键初始未定义却在结尾赋值（依赖动态添加）。
- **影响**：可读性/简洁性问题。

### [LOW-5] 折扣浮点精度

- **位置**：第 25 行 `order["amount"] * 0.9`
- **问题描述**：`0.9` 为浮点近似值，大量订单累加可能产生浮点误差（如 `0.9` 无法精确表示）。
- **影响**：金额类统计的精度风险，建议用 Decimal 或整数分。

---

## 各维度评分

| 维度 | 评分 | 说明 |
|---|---|---|
| 整洁性 | 5/10 | 重复遍历 orders 多次，result 冗余初始化，逻辑可合并 |
| 可用性 | 4/10 | 无契约文档、外部依赖耦合、副作用未声明 |
| 代码质量 | 1/10 | 4 个高严重度缺陷（漏算、崩溃、top_buyer 恒错、SQL 注入） |

---

## 修复方向建议（供修复环节参考，不代替写最终代码）

1. **HIGH-1**：遍历改为 `for order in orders`（或 `range(len(orders))`）收集全部订单金额。
2. **HIGH-2**：入口守卫空列表（返回约定空结果或抛明确 `ValueError`），保证单元素可正常处理。
3. **HIGH-3**：`top_buyer` 改为基于完整金额求最大值后取对应买家（如 `max(orders, key=lambda o: o["amount"])["name"]`），不要用「金额 > best」这种恒假条件。
4. **HIGH-4**：SQL 改为参数化查询（如 `SELECT * FROM orders WHERE buyer = ?` + 参数传入），禁止字符串拼接。
5. **MEDIUM-1**：`vip_levels=None` 哨兵 + 内部 `if vip_levels is None: vip_levels = []`。
6. **MEDIUM-2**：统计与告警分离——`summarize_orders` 只返回 `flagged` 列表，由调用方决定是否触发 `send_alert`。
7. **MEDIUM-3**：`execute_query`/`db` 通过依赖注入或参数传入，避免全局未定义依赖。
8. **LOW**：补 docstring 契约、合并重复遍历、直接构造 result、金额用 Decimal/整数。

---

## 验证记录

原始代码文件：`workspace/original_summarize_orders.py`（证据保留）
验证脚本：`workspace/verify_original.py`、`workspace/verify_sql_injection.py`（db/send_alert 已打桩）

```text
$ python3 workspace/verify_original.py
空列表 []            -> EXCEPTION IndexError: list index out of range
单元素 [A:100]       -> EXCEPTION IndexError: list index out of range
[A:1000,B:100,C:2000] -> {'top_buyer': 'A', 'avg': 1050.0}  期望 top_buyer='C', avg=1500.0  FAIL
[A:50,B:1000,C:3000]  -> {'top_buyer': 'A', 'avg': 2000.0}   期望 top_buyer='C'             FAIL
send_alert 调用: ['C']（统计函数内触发副作用）

$ python3 workspace/verify_sql_injection.py
恶意买家名 "x' OR '1'='1" -> SQL: "SELECT * FROM orders WHERE buyer = 'x' OR '1'='1'"  SQL 注入确认
默认 vip_levels 对象共享确认（同一对象 id）
```
