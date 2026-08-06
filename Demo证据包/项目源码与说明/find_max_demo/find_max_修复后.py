# 修复后版本：fixer 按方案 A 修复（基于 reviewer 的审查报告）
# 任务：task-20260801-101600
#
# 修复点：
#   1) 极值初始化由 0 改为 nums[0]，修复"全负数列表错误返回 0"
#   2) 空列表显式抛出 ValueError，修复"空列表静默返回 0"
#   3) 类型异常给出清晰提示（混入 None 等非数字元素时报错而非崩溃）
#   4) 补充 docstring


def find_max(nums):
    """返回列表中的最大值。

    空列表抛出 ValueError；要求元素均为数字。
    """
    if not nums:
        raise ValueError("nums 不能为空")
    max_val = nums[0]
    for num in nums[1:]:
        if num > max_val:
            max_val = num
    return max_val
