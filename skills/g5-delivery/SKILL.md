---
name: g5-delivery
description: 终报强制交付协议——任务完成时按机械步骤把完整终报（G5 最终汇总）发送到【任务发起房间】，并确认发送成功后才宣告完成。解决"终报只发团队房间不回发起房间"的执行层问题。
assign_when: orchestrator 需要在任务完成时输出终报、或任何需要把完成报告回执给任务发起人的场景。
---

# 终报强制交付协议（g5-delivery）

## 触发时机

**每次任务完成、准备发出终报时，必须执行本协议。** 不得跳过、不得用团队房间通知替代。

## 机械步骤（缺一不可）

### 第 1 步：确认发起房间

从任务记录中确认**发起房间**：
- Admin 在 Leader DM（!uWCQUypVR6vE5wjiYr:matrix-local.agentteams.io:18080）发任务 → 发起房间 = Leader DM
- Admin 在团队房间发任务 → 发起房间 = 团队房间
- Manager 在 Leader 房间派发 → 发起房间 = Leader 房间

### 第 2 步：组装完整终报（G5 最终汇总）

按 shared-state-board 铁律组装：
- 完整交付代码**逐字粘贴**（严禁契约示意块）
- return 键逐一核对（每个键都有真实赋值）
- 边界用例**实跑输出**（空列表 / None / 单元素）
- 任务闭环（无 commit/push 等待提示）

### 第 3 步：发送到发起房间（硬性）

```bash
copaw channels send --agent-id default --channel matrix \
  --target-user @blue:matrix-local.agentteams.io:18080 \
  --target-session <发起房间 ID> \
  --text "<完整终报>"
```

- 发起房间 = Leader DM 时，`--target-session` 必须是 `!uWCQUypVR6vE5wjiYr:matrix-local.agentteams.io:18080`
- **发送成功才算任务完成**

### 第 4 步：验证并闭环

- 确认发送返回成功（有 messageId）
- 团队房间可另行发简要完成通知（可选，不替代发起房间的完整终报）
- 发送失败 → **先报告 Manager**，不得只在团队房间发完就宣告完成

## 常见执行失误（禁止重犯）

| 错误 | 正确 |
|------|------|
| 按旧习惯把终报只发到团队房间 | 必须发回**发起房间** |
| 发了团队房间就宣告完成 | 先发发起房间，成功后才算完成 |
| 忘了记录发起房间 | 收到任务瞬间先记下，全程携带 |
| 用简要通知替代完整报告 | 发起房间必须收到**完整终报** |

## 自检

- [ ] 发起房间是什么？终报发到那里了吗？
- [ ] copaw channels send 返回成功（有 messageId）？
- [ ] 团队房间通知 ≠ 发起房间的完整终报，确认没有替代？
