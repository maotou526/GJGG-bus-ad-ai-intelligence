"""
字符串处理工具类
"""
from typing import List


def split_and_strip(raw_value: str) -> List[str]:
    """
    将逗号分隔的字符串解析为列表并去除空白
    
    Args:
        raw_value: 逗号分隔的字符串
        
    Returns:
        去除空白后的字符串列表，如果输入为空则返回空列表
        
    Example:
        >>> split_and_strip("a, b, c")
        ['a', 'b', 'c']
        >>> split_and_strip("")
        []
    """
    if not raw_value:
        return []
    return [item.strip() for item in raw_value.split(",") if item.strip()]

