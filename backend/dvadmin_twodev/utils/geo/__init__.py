# -*- coding: utf-8 -*-

"""
地图几何计算工具类模块
包含地图坐标计算、几何运算等功能的工具类

@author: 王晨
@Created on: 2024/12/19
@Remark: 地图几何计算工具类模块，提供坐标转换、距离计算、几何运算等功能
"""

# 导入主要的工具类，方便外部使用
from .geo_utils import GeoCalculator, CoordConverter, GridCalculator

# 定义模块的公开接口
__all__ = [
    'GeoCalculator',    # 地图几何计算工具类
    'CoordConverter',   # 坐标系转换工具类
    'GridCalculator',   # 网格计算工具类
]

# 模块版本信息
__version__ = '1.0.0'
__author__ = '王晨'
__description__ = '地图几何计算工具类模块'
