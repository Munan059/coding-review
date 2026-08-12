---
name: mock-gateway-protocol
description: mock 网关调用协议——封装对 coding-review 团队 mock_tool_server 网关的标准 HTTP 调用方法（取待审代码 / 取测试用例 / 提交修复验证）。任何新场景只需替换 scenario_id 即可复用同一协议，无需重写调用逻辑。
assign_when: Worker 需要从 mock_tool_server 网关获取待审查代码、测试用例，或提交修复代码做自动验证时。
---

# Mock 网关调用协议（Mock Gateway Protocol）

## 网关信息

- **地址**：`http://host.docker.internal:18089`
  - 说明：`host.docker.internal` 是容器视角下访问 **Windows 主机** 的固定域名
  - 该网关为普通 HTTP 服务，**不需要 MCP 配置**，直接运行时执行 `curl` 或 `python` 发起请求即可

## 标准端点

`{scenario_id}` 为场景占位符，示例：`buggy_find_max`、`pr_security_issue`

| 方法 | 端点 | 用途 | 请求体 |
|------|------|------|--------|
| `GET` | `/scenarios/{scenario_id}/code` | 获取待审代码 | 无 |
| `GET` | `/scenarios/{scenario_id}/tests` | 获取测试用例 | 无 |
| `POST` | `/scenarios/{scenario_id}/apply_fix` | 提交修复代码并自动验证 | `{"code": "<完整的 python 模块源码>"}` |

`POST /apply_fix` 的响应包含**测试通过情况**（如通过数 / 失败数 / 是否全部通过），是回归验证的核心依据。

## 调用方式（二选一，运行时直接执行）

### 方式 A：curl

```bash
# 1. 取待审代码
curl -s http://host.docker.internal:18089/scenarios/buggy_find_max/code

# 2. 取测试用例
curl -s http://host.docker.internal:18089/scenarios/buggy_find_max/tests

# 3. 提交修复验证（注意 JSON 转义）
curl -s -X POST http://host.docker.internal:18089/scenarios/buggy_find_max/apply_fix \
  -H "Content-Type: application/json" \
  -d '{"code": "def find_max(nums):\n    ...\n"}'
```

### 方式 B：Python（urllib，无需第三方依赖）

```python
import json, urllib.request

BASE = "http://host.docker.internal:18089"
scenario = "buggy_find_max"

def get_code(scenario_id=scenario):
    with urllib.request.urlopen(f"{BASE}/scenarios/{scenario_id}/code") as r:
        return r.read().decode()

def get_tests(scenario_id=scenario):
    with urllib.request.urlopen(f"{BASE}/scenarios/{scenario_id}/tests") as r:
        return r.read().decode()

def apply_fix(code, scenario_id=scenario):
    req = urllib.request.Request(
        f"{BASE}/scenarios/{scenario_id}/apply_fix",
        data=json.dumps({"code": code}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read().decode())
```

> 若环境装有 `requests`，可用 `requests.get/post` 等价实现。

## 复用规则

1. **任何新场景只需替换 `scenario_id`**（如把 `buggy_find_max` 换成 `pr_security_issue`），同一套端点、同一套调用代码直接套用，**无需重写**
2. `{scenario_id}` 由任务 / orchestrator 指定，或从共享状态板的 `scenario_id` 字段读取
3. 调用失败（网络 / 4xx / 5xx）时：重试 1 次；仍失败则按异常流程上报 orchestrator，不擅自猜测结果

## 配合执行模型（重要）

- **回归验证在 G3 阶段内自动执行**：拿到修复代码后，直接调用 `apply_fix` 验证，**不触发写操作门禁**（本技能只做 HTTP 调用与验证，不涉及 commit / push / merge 等仓库写操作）
- 验证结果按 `test_result`（ran / passed / regression / note）格式写入共享状态板，并通知 orchestrator
- 测试不通过 → 通过 communication 上报 orchestrator，请求打回 fixer 重做

## 故障排查（连接失败时按序检查）

| 现象 | 检查项 | 处理 |
|------|--------|------|
| 所有端点 HTTP 000 / 连接超时 | 网关服务是否在运行 | 在主机执行 `netstat -ano \| findstr 18089`，无输出 = 服务未启动，需先启动 mock_tool_server |
| 主机能看到监听但容器连不上 | 监听地址是否为 `0.0.0.0:18089` | 若只监听 `127.0.0.1`，需改为监听 `0.0.0.0` |
| 容器仍连不上 | 主机防火墙是否放行 18089 | 放行 Windows 防火墙入站规则（TCP 18089） |
| 返回 404 | 端点路径或 scenario_id 拼写错误 | 核对 `/scenarios/{scenario_id}/code` 与任务指定的 scenario_id |
| 返回 4xx/5xx | 请求体格式错误 | `POST apply_fix` 必须携带 `{"code": "<完整源码>"}` 且 `Content-Type: application/json` |

排查后仍失败：重试 1 次 → 仍失败则按异常流程上报 orchestrator，不擅自猜测结果。

## 协作纪律

- 只读运行 + 提交修复验证，**不自动提交代码**、不执行任何仓库写操作
- 所有调用与结果记录在共享状态板，保证可回溯
- 遇需审批 / 异常，即刻上报 orchestrator，未收到明确执行指令绝不擅自行动
