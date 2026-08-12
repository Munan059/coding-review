---
name: shared-state-board
description: 共享状态板与终报规范——定义四个 Agent 共用的白板字段分工（谁写谁）、传递纪律、G5 最终报告模板与自检要求。orchestrator 用它维护状态板、汇总成员产出并输出终报。
assign_when: orchestrator 需要维护共享状态板、协调成员写入顺序、或输出 G5 最终汇总报告时。
---

# 共享状态板与终报规范（Shared State Board）

## 一、白板是四个 Agent 的传递通道

- reviewer / fixer / tester 把各自产出写进**同一块白板**，orchestrator 在白板上**全能看到**
- orchestrator 的**最终报告**从白板上三个人的产出里**汇总**出来，**不在群里另说一遍**（群聊只做阶段汇报与提醒，内容以白板为准）

## 二、白板字段（谁写谁）

| Agent | 字段 | 说明 |
|-------|------|------|
| **orchestrator** | `task_id` | 任务标识 |
| | `scenario_id` | 场景标识（如 buggy_find_max） |
| | `status` | 待审 → 修复中 → 测试中 → 完成 / 打回 |
| | `current_gate` | 当前关卡（G1~G5） |
| | `ack_status` | 待你确认 / 已确认 |
| **reviewer** | `review_report` | 带行号 + 高 / 中 / 低 严重级别 |
| **fixer** | `fixed_code` | 改进后的代码 |
| **tester** | `test_result` | ran / passed / regression / note |

## 三、纪律

1. **每个 Agent 只写自己的字段，不碰别人的**
2. **串行依赖**：fixer 等 reviewer 写完再动手；tester 等 fixer 写完再跑；orchestrator 等三者齐了再终报
3. **没写到的标「待补充」**，绝不瞎编、不脑补缺失字段

## 四、G5 终报模板（每项都从白板取，不编）

```markdown
【代码审查终报】task_id=xxx / scenario_id=xxx

1. 状态：status=完成 / current_gate=G5 / ack_status=已闭环
2. 审查结论（取 review_report）：高 N／中 N／低 N
3. 修复说明（取 fixed_code）：改了啥、为啥 + 【完整交付代码原文】
4. 验证结果（取 test_result）：跑 N／过 N／回归一致？+ 【边界用例实跑输出】
5. 遗留风险与建议
6. 任务闭环（不再请求 ACK；如需 commit/push，Admin 会另行 @mention 指示）
```

**铁律（每次 G5 必须逐条执行）**：
1. 第 2~4 节的每一项数据必须**从白板对应字段读取**，不允许凭记忆或群聊内容编造。
2. **完整代码逐字粘贴**：代码展示必须是交付文件（fixed_*.py）的**完整、可直接运行的源代码**，逐字粘贴，不得省略任何赋值或函数体；**严禁「契约示意块」**（只写注释、把关键计算略掉的写法）。
3. **return 键逐一核对**：出终报前，逐字段核对 return 字典里的**每个键是否都在函数体里有真实定义与赋值**；只要有一个没算（如 discount_total 只注释没赋值），就**打回 fixer 补全**，不准出报告。
4. **边界用例贴实结果**：空列表 / None / 单元素 等场景，报告必须贴**实际运行输出**，不能只写注释「已处理」。
5. **tester 实跑门禁**：G5 之前，tester 必须用 python **实跑交付文件**，确认无 NameError / 语法错误、能正常返回，才允许出终报。
6. **汇报回执原则**：G5 终报（及各阶段汇报）**必须发回任务发起房间**——Admin 在 Leader DM 发任务则发回 Leader DM（@Admin），在团队房间发则发回团队房间，Manager 在 Leader 房间派发则发回 Leader 房间；**绝不允许 G5 只发到团队房间而不回发起房间**，让发起人无需切换页面即可收到完成报告。
7. **G5 直接闭环**：任务完成即结束，终报**不得**包含「如需 commit/push 请回复继续/ACK」之类的等待提示；写操作只在 Admin 事后单独 @mention 时才另行执行。

## 五、白板实现（具体落地，取代"仅概念"）

白板 = 团队共享区的一个 **JSON 数据文件**：`shared/state-board/{task_id}.json`

```json
{
  "task_id": "rank-students-review-20260805-050346",
  "scenario_id": "rank_students",
  "status": "待审 | 修复中 | 测试中 | 完成 | 打回",
  "current_gate": "G1 | G2 | G3 | G4 | G5",
  "ack_status": "待确认 | 已确认",
  "review_report": "「待补充」或审查结论摘要（高N/中N/低N + 关键发现）",
  "fixed_code": "「待补充」或修复说明（改了啥、为啥，指向实际代码文件）",
  "test_result": "「待补充」或 ran/passed/regression/note"
}
```

落地协议：
1. **orchestrator 在 G1 创建** `shared/state-board/{task_id}.json`，维护 `task_id / scenario_id / status / current_gate / ack_status`
2. **reviewer / fixer / tester** 各自 `filesync` 拉取后，**只更新自己的字段**（review_report / fixed_code / test_result），再 `filesync` 推送
3. 未写到的字段标 **「待补充」**，不瞎编
4. G5 终报的每一项数据必须从该 JSON 读取，不得凭记忆或聊天内容编造

## 六、自检（终报发出前逐项确认）

- [ ] 白板文件存在且三个人的字段（review_report / fixed_code / test_result）都写齐了？缺的标了「待补充」？
- [ ] 每节内容都来自白板 JSON？
- [ ] `status` 与 `current_gate` 一致（如 status=测试中 时 gate 应为 G3）？
- [ ] `ack_status` 是否正确反映"需用户确认 / 已确认"？

## 七、G5 回执门禁（Admin 明确要求，任务闭环的硬条件）

**任务未把 G5 发到发起房间并确认成功之前，不得宣告任务完成。** 具体：

1. **白板新增字段** `g5_delivered_message_id`：G5 成功发到发起房间后，记录发送返回的 messageId；未发送时标「待回执」。
2. **状态机绑定**：
   - G5 组装完成但未发送到发起房间 → 白板 `status` = `完成待回执`，`ack_status` = `待回执`
   - G5 成功发到发起房间（有 messageId）→ `status` = `完成`，`ack_status` = `已回执`
   - **不得**在未回执时把 status 置为 `完成`
3. **证据要求**：每次 G5 回执后，在报告/白板中写明 messageId 作为证据，Manager 可据此核验。
4. **失败处理**：发送失败 → 先报告 Manager，不得宣告完成。

## 八、自检（G5 回执门禁）

- [ ] `g5_delivered_message_id` 已填写（非「待回执」）？
- [ ] G5 发送到了**发起房间**（不是只发团队房间）？
- [ ] `status` 是否为 `完成` 且 `ack_status` 为 `已回执`？

## 协作纪律

- 只维护白板与汇报，不替 reviewer / fixer / tester 代写字段
- 成员字段缺失或异常 → 先核实再上报，不猜测
- 写操作（commit / push / merge）不在此技能范围，仅当 Admin 明确要求时执行
