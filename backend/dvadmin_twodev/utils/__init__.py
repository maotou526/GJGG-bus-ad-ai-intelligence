# -*- coding: utf-8 -*-

"""
太仓线网业务工具类模块
包含地图几何计算、坐标转换等业务相关的工具类

模块结构：
- geo/          - 地图几何计算相关工具类
  - geo_utils.py     - 核心几何计算工具类
  - geo_examples.py  - 使用示例
  - test_geo_utils.py - 单元测试
  - README.md        - 详细说明文档
- math/         - 数学计算相关工具类
  - calculation_utils.py - 计算工具函数（百分比计算等）
"""

# 导入子模块，方便外部使用
from . import geo
from . import math

# 定义模块的公开接口
__all__ = [
    'geo',   # 地图几何计算模块
    'math',  # 数学计算模块
]

# 模块版本信息
__version__ = '1.0.0'
__author__ = '王晨'
__description__ = '太仓线网业务工具类模块'
