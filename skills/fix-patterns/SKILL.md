---
name: fix-patterns
description: 修复技能（缺陷→修复模式）——基于 reviewer 的 review_report 按严重级别排序修复，内置六类常见缺陷的 before/after 修复模式映射、修复总原则与输出自检清单。适用于任何"依据审查报告修复代码"的场景。
assign_when: Worker 需要根据审查报告生成修复代码（fixer 角色的核心技能），或任何"按缺陷清单修复代码"的任务。
---

# 修复技能：缺陷 → 修复模式（Fix Patterns）

## 一、输入约定（先读什么、按什么顺序修）

1. 从**共享状态板**读取 reviewer 的 **`review_report`**（结构：每条发现含 **行号 / 严重级别 / 维度 / 问题描述 / 修复建议**）
2. 按严重级别排序修复：**阻断（高）→ 警告（中）→ 提示（低）**；同级别内按行号从小到大
3. 每条修复完成后，在报告中标记对应发现（`fixed: 行号`），确保审查发现的**闭环**（无遗漏、无悬空）
4. 若 review_report 缺失或格式不完整，先上报 orchestrator，不凭空猜测修复目标

## 二、修复总原则（永远遵守）

| 原则 | 说明 |
|------|------|
| **最小改动** | 只改有问题的行/块，不顺手重构无关代码 |
| **不改接口语义** | 函数签名、返回值类型、调用方契约保持不变（除非审查明确要求） |
| **保持可读性** | 修复后的代码清晰、命名可读、必要时补充注释 |
| **绝不自动合主干** | 只生成/提交改进代码，不自动 merge 主分支；commit / push / merge 仅当 Admin 通过 orchestrator 明确要求才执行 |

## 三、缺陷类型 → 修复模式映射表（含 before/after）

> 两条 demo 场景贯穿示例：`buggy_find_max`（find_max 函数）与 `pr_security_issue`（安全场景）

### 1️⃣ 边界条件缺失 → 加前置校验或默认值

```python
# ❌ before（buggy_find_max 的根因：max_val=0 硬编码，全负数列表错误返回 0）
def find_max(nums):
    max_val = 0
    for n in nums:
        if n > max_val:
            max_val = n
    return max_val

# ✅ after（用首个元素作初始值，消除对 0 的隐式依赖）
def find_max(nums):
    if not nums:
        raise ValueError("nums 不能为空")
    max_val = nums[0]
    for n in nums[1:]:
        if n > max_val:
            max_val = n
    return max_val
```

### 2️⃣ 空值 / None 未处理 → 守卫判断（Guard Clause）

```python
# ❌ before：空列表/None 静默返回 0，行为未定义
def avg(nums):
    return sum(nums) / len(nums)   # len=0 时 ZeroDivisionError

# ✅ after：前置守卫，明确契约
def avg(nums):
    if not nums:
        raise ValueError("nums 不能为空")
    return sum(nums) / len(nums)

# None 场景同理：
def get_user_name(user):
    if user is None or user.name is None:
        return "unknown"
    return user.name
```

### 3️⃣ 安全类：SQL 注入 → 参数化查询（绝不字符串拼接）

```python
# ❌ before（pr_security_issue 的典型问题：字符串拼接可被注入）
def query_user(name):
    cursor.execute(f"SELECT * FROM users WHERE name='{name}'")

# ✅ after：参数化查询
def query_user(name):
    cursor.execute("SELECT * FROM users WHERE name = %s", (name,))
    # SQLite/MySQL 用 %s；PostgreSQL 用 %s；SQL Server 用 %s 或 ?（按驱动约定）
```

> 安全类缺陷一律按**阻断级**处理；任何 `字符串拼接 SQL / 拼接 shell 命令 / eval` 都必须改为参数化或白名单校验。

### 4️⃣ 重复代码 → 提取函数

```python
# ❌ before：两处重复校验逻辑
def create_user(data):
    if not data.get("name") or len(data["name"]) > 50:
        raise ValueError("invalid name")
    ...
def update_user(data):
    if not data.get("name") or len(data["name"]) > 50:
        raise ValueError("invalid name")
    ...

# ✅ after：提取公共函数
def _validate_name(data):
    if not data.get("name") or len(data["name"]) > 50:
        raise ValueError("invalid name")

def create_user(data):
    _validate_name(data); ...
def update_user(data):
    _validate_name(data); ...
```

### 5️⃣ 命名混乱 → 语义化重命名

```python
# ❌ before
tmp = [x * 2 for x in items]
res = calc(tmp)

# ✅ after
doubled_items = [x * 2 for x in items]
total_price = calc(doubled_items)
```

> 重命名只做局部、机械替换，保证引用处同步更新，不改行为。

### 6️⃣ 潜在缺陷（除零 / 越界 / 资源泄漏）→ 防御性检查

```python
# ❌ before：除零
def ratio(total, count):
    return total / count

# ✅ after：防御性检查
def ratio(total, count):
    if count == 0:
        return 0.0   # 或 raise ValueError，按业务契约
    return total / count

# ❌ before：列表越界
def first_or_default(items):
    return items[0]

# ✅ after
def first_or_default(items):
    return items[0] if items else None
```

## 四、输出约定 + 自检清单

### 输出约定

1. 改进代码写入共享状态板的 **`fixed_code` 字段**，同时落盘为 `workspace/fixed_code.py`（或对应文件）
2. 输出**修复说明**：每条修复对应 review_report 的哪个发现（行号 + 严重级别 + 修复方式摘要）
3. 完成后通知 orchestrator，等待派发 tester 回归

### 修复后自检清单（逐项确认）

- [ ] **未引入新问题**：改动是否会影响其他调用方？是否新增了越界 / 除零 / 类型错误风险？
- [ ] **能过 tester 回归**：修复代码能否通过 mock 网关 `apply_fix` 验证（或本地测试）？若无法自测，明确标注"待 tester 验证"
- [ ] **最小改动**：是否只动了必要范围？有没有顺手改无关逻辑？
- [ ] **接口语义不变**：函数签名 / 返回值契约是否保持？
- [ ] **无写操作越界**：本阶段只生成代码，未执行 commit / push / merge

### 协作纪律

- 生成修复代码后**不自动提交**，等待 orchestrator 指示（仅当 Admin 明确要求时才执行写操作）
- 遇需审批 / 异常（如无法定位问题代码、review_report 矛盾）→ 即刻上报 orchestrator，未收到明确执行指令绝不擅自行动
