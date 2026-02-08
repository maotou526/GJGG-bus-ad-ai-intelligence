# -*- coding: utf-8 -*-

"""
太仓线网常量定义模块
包含系统常量和业务常量

@author: 王晨
@Created on: 2024/12/19
@Remark: 常量定义模块，提供系统常量和业务常量
"""

# 导入常量模块，方便外部使用
from . import system_constants
from . import business_constants

# 定义模块的公开接口
__all__ = [
    'system_constants',    # 系统常量模块
    'business_constants',  # 业务常量模块
]

# 模块版本信息
__version__ = '1.0.0'
__author__ = '王晨'
__description__ = '太仓线网常量定义模块'
