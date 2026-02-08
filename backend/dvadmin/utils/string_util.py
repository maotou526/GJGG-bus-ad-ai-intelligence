# -*- coding: utf-8 -*-

"""
@author: 猿小天
@contact: QQ:1638245306
@Created on: 2021/8/21 021 9:48
@Remark:
"""
import hashlib
import random
from datetime import datetime, date

CHAR_SET = ("2", "3", "4", "5",
            "6", "7", "8", "9", "A", "B", "C", "D", "E", "F", "G", "H",
            "J", "K", "L", "M", "N", "P", "Q", "R", "S", "T", "U", "V",
            "W", "X", "Y", "Z")


def random_str(number=16):
    """
    返回特定长度的随机字符串(非进制)
    :return:
    """
    result = ""
    for i in range(0, number):
        inx = random.randint(0, len(CHAR_SET) - 1)
        result += CHAR_SET[inx]
    return result


def has_md5(str, salt='123456'):
    """
    md5 加密
    :param str:
    :param salt:
    :return:
    """
    # satl是盐值，默认是123456
    str = str + salt
    md = hashlib.md5()  # 构造一个md5对象
    md.update(str.encode())
    res = md.hexdigest()
    return res


def get_date_object(date_value):
    """
    将日期值转换为日期对象
    支持字符串和日期对象
    
    :param date_value: 日期值，可以是字符串或日期对象
    :return: 日期对象或None
    """
    if not date_value:
        return None
    
    if isinstance(date_value, str):
        try:
            # 尝试解析 YYYY-MM-DD 格式
            return datetime.strptime(date_value, '%Y-%m-%d').date()
        except ValueError:
            try:
                # 尝试解析 YYYY-MM-DD HH:MM:SS 格式
                return datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S').date()
            except ValueError:
                try:
                    # 尝试解析 YYYY-MM-DDTHH:MM:SS 格式（ISO格式）
                    return datetime.strptime(date_value, '%Y-%m-%dT%H:%M:%S').date()
                except ValueError:
                    return None
    elif isinstance(date_value, datetime):
        return date_value.date()
    elif isinstance(date_value, date):
        return date_value
    else:
        return None


def format_date_for_display(date_value, format_str='%Y-%m-%d'):
    """
    格式化日期用于显示
    
    :param date_value: 日期值
    :param format_str: 格式字符串
    :return: 格式化后的日期字符串
    """
    date_obj = get_date_object(date_value)
    if date_obj:
        return date_obj.strftime(format_str)
    return None


def parse_list_param(raw_value):
    """
    将逗号分隔的字符串解析为列表并去除空白
    
    :param raw_value: 逗号分隔的字符串
    :return: 去除空白后的字符串列表，如果输入为空则返回空列表
    
    Example:
        >>> parse_list_param("a, b, c")
        ['a', 'b', 'c']
        >>> parse_list_param("")
        []
    """
    if not raw_value:
        return []
    return [item.strip() for item in str(raw_value).split(",") if item.strip()]