# 原始版本：被 reviewer 审查出 2 个严重 bug
# 任务：task-20260801-101600（devteam 端到端流水线：审查 → 修复 → 测试）


def find_max(nums):
    max_val = 0
    for num in nums:
        if num > max_val:
            max_val = num
    return max_val
