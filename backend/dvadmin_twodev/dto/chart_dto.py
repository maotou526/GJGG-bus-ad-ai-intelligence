"""
图表相关DTO
用于定义图表显示的数据结构
"""

from dataclasses import dataclass
from typing import Union


@dataclass
class ChartPointDTO:
    """
    图表坐标点DTO
    只包含X轴和Y轴数据，其他图表配置由前端处理
    
    Attributes:
        x: X轴值，支持字符串、整数、浮点数
        y: Y轴值，支持字符串、整数、浮点数
    """
    x: Union[str, int, float]  # X轴值
    y: Union[str, int, float]  # Y轴值
