# -*- coding: utf-8 -*-

"""
计算工具函数
包含百分比计算、数据对比等计算相关的工具函数
"""


def calculate_change_percentage(current, previous):
    """
    计算数据变化百分比
    
    参数：
    - current: 当前值
    - previous: 上一期值
    
    返回：
    {
        'percentage': 百分比值（正数表示增长，负数表示下降）,
        'trend': 'up' (增长) / 'down' (下降) / 'flat' (持平),
        'display': 显示文本（如 '+2%' 或 '-15%' 或 '持平'）
    }
    
    示例：
    >>> result = calculate_change_percentage(105, 100)
    >>> result['percentage']
    5.0
    >>> result['trend']
    'up'
    >>> result['display']
    '+5%'
    
    >>> result = calculate_change_percentage(90, 100)
    >>> result['percentage']
    -10.0
    >>> result['trend']
    'down'
    >>> result['display']
    '-10%'
    
    >>> result = calculate_change_percentage(100, 100)
    >>> result['trend']
    'flat'
    >>> result['display']
    '持平'
    """
    if previous == 0:
        if current == 0:
            return {'percentage': 0, 'trend': 'flat', 'display': '持平'}
        else:
            # 从0增长到非0，视为100%增长
            return {'percentage': 100, 'trend': 'up', 'display': '+100%'}
    
    percentage = ((current - previous) / previous) * 100
    
    if percentage > 0:
        trend = 'up'
        display = f"+{percentage:.0f}%"
    elif percentage < 0:
        trend = 'down'
        display = f"{percentage:.0f}%"
    else:
        trend = 'flat'
        display = '持平'
    
    return {
        'percentage': percentage,
        'trend': trend,
        'display': display
    }

