# -*- coding: utf-8 -*-

'''
Description: Excel线路数据解析工具
Version: 1.0
Author: 王晨
Date: 2025-12-27 13:31:36
LastEditors: 王晨
LastEditTime: 2025-12-27 14:24:25
'''
import os
from typing import List, Dict, Optional, Tuple
import openpyxl
import time
from datetime import datetime
import requests
from difflib import SequenceMatcher
import re

# ============================================
# 高德地图API配置 - 请在此处填写你的API密钥
# ============================================
AMAP_API_KEY = "40d167564ff31e9c1a7ead7d30e407be"  # 高德地图API密钥
AMAP_BASE_URL = "https://restapi.amap.com"
AMAP_CITY_CODE = "320585"  # 城市adcode，320000代表江苏省，320585代表太仓市


def call_gaode_bus_line_name(keywords: str, city: str, api_key: str = None) -> Dict:
    """
    调用高德地图公交路线关键字查询API
    
    Args:
        keywords: 线路名称关键字
        city: 城市adcode（如：320000代表江苏省）
        api_key: 高德API密钥，不传则使用全局配置
        
    Returns:
        dict: API返回的JSON数据
    """
    key = api_key or AMAP_API_KEY
    if not key or key == "YOUR_AMAP_API_KEY":
        raise ValueError("请先配置高德地图API密钥 AMAP_API_KEY")
    
    url = f"{AMAP_BASE_URL}/v3/bus/linename"
    params = {
        'key': key,
        'keywords': keywords,
        'city': city,
        'extensions': 'all',
        'output': 'JSON'
    }
    
    response = requests.get(url, params=params, timeout=30)
    data = response.json()
    
    # 检查API返回状态
    if data.get('status') != '1':
        error_info = data.get('info', '未知错误')
        error_code = data.get('infocode', '')
        raise Exception(f"高德地图API错误: {error_info} (错误码: {error_code})")
    
    return data


def parse_roadline_excel(excel_path: str) -> List[Dict]:
    """
    解析线路表Excel文件
    
    Args:
        excel_path: Excel文件路径
        
    Returns:
        List[Dict]: 解析后的数据列表，每个字典包含一行数据，主要包含"线路名称"字段
        
    Raises:
        FileNotFoundError: Excel文件不存在
        ValueError: Excel文件格式错误或缺少必要的列
    """
    # 检查文件是否存在
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel文件不存在: {excel_path}")
    
    # 打开Excel文件
    workbook = openpyxl.load_workbook(excel_path, data_only=True)
    
    # 获取第一个sheet（sheet1），在openpyxl中sheet索引从0开始
    # 注意：用户提到要将sheet1改名叫"太仓全部线路信息"，这里我们读取第一个sheet
    # 如果需要重命名sheet，可以在读取后重命名，但为了不影响原文件，这里只是读取
    sheet = workbook[workbook.sheetnames[0]]
    
    # 定义表头字段列表（按照用户提供的顺序）
    header_fields = [
        "营运公司", "分公司", "线路名称", "线路编码", "上/下行", "启用日期", 
        "线路负责人", "电话", "办公地址", "负责人电话", "线路长度（公里）", 
        "上/下行线路长度（公里）", "GPS公里", "始发站地址", "始发站电话", 
        "始发站", "始发站头班车时间", "始发站末班车时间", "票价形式", 
        "平日计划全程行驶时间(分)", "平日计划高峰班次平均间隔时间(分)", 
        "平日计划低谷班次平均间隔时间(分)", "平日计划配车数", "撤销日期", 
        "线路走向", "是否旅游线", "是否隧道线", "隧道名称", "是否大桥线", 
        "大桥名称", "是否机场线", "机场名称", "是否环线", "营运状态", 
        "最后更新日期", "票价类型", "价目表", "权证数", "配车数", "等级线路", 
        "大间隔", "日均人次", "日均营收", "计划班次", "备注"
    ]
    
    # 读取表头行（第一行）
    header_row = []
    for cell in sheet[1]:
        header_value = cell.value
        if header_value:
            # 去除空格和换行符
            header_value = str(header_value).strip()
        else:
            header_value = ""
        header_row.append(header_value)
    
    # 创建表头字段到列索引的映射
    header_map = {}
    for idx, header in enumerate(header_row, start=1):
        if header:
            header_map[header] = idx
    
    # 检查必要的字段是否存在（主要是"线路名称"）
    if "线路名称" not in header_map:
        raise ValueError("Excel文件中未找到'线路名称'列，请检查Excel文件格式")
    
    # 解析数据行
    result_data = []
    # 从第二行开始读取数据（第一行是表头）
    for row_idx in range(2, sheet.max_row + 1):
        row_data = {}
        
        # 遍历所有表头字段，提取对应的列数据
        for field in header_fields:
            if field in header_map:
                col_idx = header_map[field]
                cell = sheet.cell(row=row_idx, column=col_idx)
                cell_value = cell.value
                
                # 处理空值
                if cell_value is None:
                    row_data[field] = None
                else:
                    # 转换为字符串并去除空格
                    if isinstance(cell_value, (int, float)):
                        # 如果是数字，检查是否是整数
                        if isinstance(cell_value, float) and cell_value.is_integer():
                            row_data[field] = str(int(cell_value))
                        else:
                            row_data[field] = str(cell_value)
                    else:
                        row_data[field] = str(cell_value).strip()
            else:
                # 如果Excel中不存在该字段，设置为None
                row_data[field] = None
        
        # 只有当"线路名称"不为空时才添加到结果中
        line_name = row_data.get("线路名称")
        if line_name and str(line_name).strip():
            result_data.append(row_data)
    
    return result_data


def get_line_names(excel_path: str) -> List[str]:
    """
    从Excel文件中提取所有线路名称
    
    Args:
        excel_path: Excel文件路径
        
    Returns:
        List[str]: 线路名称列表（去重后的）
    """
    data = parse_roadline_excel(excel_path)
    line_names = [item["线路名称"] for item in data if item.get("线路名称")]
    # 去重并保持顺序
    seen = set()
    unique_line_names = []
    for name in line_names:
        if name not in seen:
            seen.add(name)
            unique_line_names.append(name)
    return unique_line_names


def get_sheet_names_from_excel(excel_path: str) -> List[str]:
    """
    从Excel文件中获取所有sheet名称（作为线路名称）
    
    Args:
        excel_path: Excel文件路径
        
    Returns:
        List[str]: sheet名称列表（即线路名称列表）
    """
    # 检查文件是否存在
    if not os.path.exists(excel_path):
        raise FileNotFoundError(f"Excel文件不存在: {excel_path}")
    
    # 打开Excel文件（只读取，不加载数据）
    workbook = openpyxl.load_workbook(excel_path, read_only=True)
    
    # 获取所有sheet名称
    sheet_names = workbook.sheetnames
    
    workbook.close()
    
    return sheet_names


def filter_buslines_by_name(buslines: List[Dict], line_name: str) -> tuple:
    """
    根据线路名称过滤公交线路结果
    
    Args:
        buslines: 高德API返回的公交线路列表
        line_name: 要匹配的线路名称
        
    Returns:
        tuple: (过滤后的公交线路列表, 是否进行了过滤, 是否有匹配)
    """
    if not buslines:
        return [], False, False
    
    # 判断线路名称是否是纯数字，如果是则在前面加上"太仓"
    compare_name = line_name
    if line_name.isdigit():
        compare_name = f"太仓{line_name}"
    
    # 比对结果，查找匹配的线路
    matched_lines = []
    for busline in buslines:
        busline_name = busline.get('name', '')
        # 比对名称（包含关系）
        if compare_name in busline_name or busline_name in compare_name:
            matched_lines.append(busline)
    
    # 如果没有匹配的，返回所有结果；否则返回匹配的结果
    has_match = len(matched_lines) > 0
    if not has_match:
        return buslines, True, False  # 返回所有结果，表示进行了过滤但无匹配
    else:
        return matched_lines, True, True  # 返回匹配的结果


def query_bus_lines_from_gaode(excel_path: str, city: str = '320000', output_file: Optional[str] = None, api_key: str = None) -> str:
    """
    从Excel中读取线路名称，调用高德地图API查询公交线路信息，并输出结果
    
    Args:
        excel_path: Excel文件路径
        city: 城市adcode，默认'320000'（江苏省）
        output_file: 输出文件路径，如果为None则自动生成
        api_key: 高德API密钥，不传则使用全局配置
        
    Returns:
        str: 查询结果文本
    """
    # 获取所有线路名称
    print(f"正在解析Excel文件: {excel_path}")
    line_names = get_line_names(excel_path)
    total_count = len(line_names)
    print(f"共找到 {total_count} 个不同的线路名称")
    
    # 准备输出文本
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append(f"公交线路高德地图API查询结果")
    output_lines.append(f"查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append(f"城市代码: {city}")
    output_lines.append(f"总线路数: {total_count}")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # 统计信息
    success_count = 0
    no_data_count = 0
    error_count = 0
    
    # 遍历每个线路名称进行查询
    for idx, line_name in enumerate(line_names, 1):
        print(f"[{idx}/{total_count}] 正在查询: {line_name}", end=" ... ")
        
        try:
            # 调用高德API查询
            result = call_gaode_bus_line_name(
                keywords=line_name,
                city=city,
                api_key=api_key
            )
            
            # 处理查询结果
            # 注意：高德API返回status为'1'表示成功，'0'表示失败
            status = result.get('status', '0')
            buslines = result.get('buslines', [])
            
            if status == '1' and buslines:
                # 过滤结果，根据线路名称进行比对
                filtered_buslines, is_filtered, has_match = filter_buslines_by_name(buslines, line_name)
                original_count = len(buslines)
                filtered_count = len(filtered_buslines)
                
                # 成功找到数据
                output_lines.append(f"{idx}. 线路名称: {line_name}")
                output_lines.append(f"   查询状态: 成功")
                output_lines.append(f"   原始找到线路数: {original_count}")
                if is_filtered:
                    output_lines.append(f"   过滤后线路数: {filtered_count}")
                    if not has_match:
                        output_lines.append(f"   说明: 未找到匹配的线路，显示所有结果")
                    else:
                        output_lines.append(f"   说明: 已过滤，只显示匹配的线路")
                
                # 输出每条线路的详细信息
                for bus_idx, busline in enumerate(filtered_buslines, 1):
                    output_lines.append(f"   └─ 线路{bus_idx}:")
                    output_lines.append(f"      ID: {busline.get('id', '无')}")
                    output_lines.append(f"      名称: {busline.get('name', '无')}")
                    output_lines.append(f"      类型: {busline.get('type', '无')}")
                    # 注意：高德API返回的字段名可能是 start_stop 和 end_stop
                    start_stop = busline.get('start_stop') or busline.get('startstop') or '无'
                    end_stop = busline.get('end_stop') or busline.get('endstop') or '无'
                    output_lines.append(f"      始发站: {start_stop}")
                    output_lines.append(f"      终点站: {end_stop}")
                    output_lines.append(f"      城市代码: {busline.get('citycode', '无')}")
                
                output_lines.append("")
                success_count += 1
                print("✓ 成功")
            else:
                # 没有找到数据
                output_lines.append(f"{idx}. 线路名称: {line_name}")
                output_lines.append(f"   查询状态: 无数据")
                output_lines.append(f"   说明: 高德地图API未找到该线路信息")
                info = result.get('info', '无')
                infocode = result.get('infocode', '无')
                output_lines.append(f"   返回信息: {info} (代码: {infocode})")
                output_lines.append("")
                no_data_count += 1
                print("✗ 无数据")
            
            # 添加延迟，避免请求过快
            time.sleep(0.2)
            
        except Exception as e:
            # 查询出错
            output_lines.append(f"{idx}. 线路名称: {line_name}")
            output_lines.append(f"   查询状态: 错误")
            output_lines.append(f"   错误信息: {str(e)}")
            output_lines.append("")
            error_count += 1
            print(f"✗ 错误: {str(e)}")
    
    # 添加统计信息
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("查询统计")
    output_lines.append("=" * 80)
    output_lines.append(f"总线路数: {total_count}")
    output_lines.append(f"查询成功: {success_count}")
    output_lines.append(f"无数据: {no_data_count}")
    output_lines.append(f"查询错误: {error_count}")
    output_lines.append("=" * 80)
    
    # 生成完整文本
    result_text = "\n".join(output_lines)
    
    # 输出到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result_text)
        print(f"\n结果已保存到文件: {output_file}")
    else:
        # 如果没有指定输出文件，生成默认文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_output_file = os.path.join(
            os.path.dirname(excel_path),
            f'公交线路查询结果_{timestamp}.txt'
        )
        with open(default_output_file, 'w', encoding='utf-8') as f:
            f.write(result_text)
        print(f"\n结果已保存到文件: {default_output_file}")
    
    # 输出到控制台
    print("\n" + result_text)
    
    return result_text


def query_bus_lines_from_sheet_names(excel_path: str, city: str = None, output_file: Optional[str] = None, api_key: str = None) -> str:
    """
    从Excel文件的sheet名称中读取线路名称，调用高德地图API查询公交线路信息
    
    Args:
        excel_path: Excel文件路径
        city: 城市adcode，默认使用全局配置 AMAP_CITY_CODE
        output_file: 输出文件路径，如果为None则自动生成
        api_key: 高德API密钥，不传则使用全局配置
        
    Returns:
        str: 查询结果文本
    """
    # 使用默认配置
    if city is None:
        city = AMAP_CITY_CODE
    if api_key is None:
        api_key = AMAP_API_KEY
    
    # 获取所有sheet名称（作为线路名称）
    print(f"正在解析Excel文件: {excel_path}")
    try:
        sheet_names = get_sheet_names_from_excel(excel_path)
    except Exception as e:
        raise Exception(f"解析Excel文件失败: {str(e)}")
    
    total_count = len(sheet_names)
    print(f"共找到 {total_count} 个sheet（线路名称）")
    print(f"Sheet名称列表: {', '.join(sheet_names[:10])}{'...' if total_count > 10 else ''}")
    
    # 准备输出文本
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append(f"公交线路高德地图API查询结果（基于Sheet名称）")
    output_lines.append(f"查询时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append(f"Excel文件: {excel_path}")
    output_lines.append(f"城市代码: {city}")
    output_lines.append(f"总线路数: {total_count}")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # 统计信息
    success_count = 0
    no_data_count = 0
    error_count = 0
    
    # 遍历每个sheet名称（线路名称）进行查询
    for idx, sheet_name in enumerate(sheet_names, 1):
        print(f"[{idx}/{total_count}] 正在查询: {sheet_name}", end=" ... ")
        
        # 将sheet名称作为线路名称进行查询
        # 注意：sheet名称可能包含特殊字符，需要处理
        line_name = sheet_name.strip()
        
        try:
            # 调用高德API查询
            result = call_gaode_bus_line_name(
                keywords=line_name,
                city=city,
                api_key=api_key
            )
            
            # 处理查询结果
            status = result.get('status', '0')
            buslines = result.get('buslines', [])
            
            if status == '1' and buslines:
                # 过滤结果，根据线路名称进行比对
                filtered_buslines, is_filtered, has_match = filter_buslines_by_name(buslines, line_name)
                original_count = len(buslines)
                filtered_count = len(filtered_buslines)
                
                # 成功找到数据
                output_lines.append(f"{idx}. Sheet名称（线路名称）: {sheet_name}")
                output_lines.append(f"   查询状态: 成功")
                output_lines.append(f"   原始找到线路数: {original_count}")
                if is_filtered:
                    output_lines.append(f"   过滤后线路数: {filtered_count}")
                    if not has_match:
                        output_lines.append(f"   说明: 未找到匹配的线路，显示所有结果")
                    else:
                        output_lines.append(f"   说明: 已过滤，只显示匹配的线路")
                
                # 输出每条线路的详细信息
                for bus_idx, busline in enumerate(filtered_buslines, 1):
                    output_lines.append(f"   └─ 线路{bus_idx}:")
                    output_lines.append(f"      ID: {busline.get('id', '无')}")
                    output_lines.append(f"      名称: {busline.get('name', '无')}")
                    output_lines.append(f"      类型: {busline.get('type', '无')}")
                    start_stop = busline.get('start_stop') or busline.get('startstop') or '无'
                    end_stop = busline.get('end_stop') or busline.get('endstop') or '无'
                    output_lines.append(f"      始发站: {start_stop}")
                    output_lines.append(f"      终点站: {end_stop}")
                    output_lines.append(f"      城市代码: {busline.get('citycode', '无')}")
                
                output_lines.append("")
                success_count += 1
                print("✓ 成功")
            else:
                # 没有找到数据
                output_lines.append(f"{idx}. Sheet名称（线路名称）: {sheet_name}")
                output_lines.append(f"   查询状态: 无数据")
                output_lines.append(f"   说明: 高德地图API未找到该线路信息")
                info = result.get('info', '无')
                infocode = result.get('infocode', '无')
                output_lines.append(f"   返回信息: {info} (代码: {infocode})")
                output_lines.append("")
                no_data_count += 1
                print("✗ 无数据")
            
            # 添加延迟，避免请求过快
            time.sleep(0.2)
            
        except Exception as e:
            # 查询出错
            output_lines.append(f"{idx}. Sheet名称（线路名称）: {sheet_name}")
            output_lines.append(f"   查询状态: 错误")
            output_lines.append(f"   错误信息: {str(e)}")
            output_lines.append("")
            error_count += 1
            print(f"✗ 错误: {str(e)}")
    
    # 添加统计信息
    output_lines.append("")
    output_lines.append("=" * 80)
    output_lines.append("查询统计")
    output_lines.append("=" * 80)
    output_lines.append(f"总线路数: {total_count}")
    output_lines.append(f"查询成功: {success_count}")
    output_lines.append(f"无数据: {no_data_count}")
    output_lines.append(f"查询错误: {error_count}")
    output_lines.append("=" * 80)
    
    # 生成完整文本
    result_text = "\n".join(output_lines)
    
    # 输出到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result_text)
        print(f"\n结果已保存到文件: {output_file}")
    else:
        # 如果没有指定输出文件，生成默认文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_output_file = os.path.join(
            os.path.dirname(excel_path),
            f'公交线路查询结果_Sheet名称_{timestamp}.txt'
        )
        with open(default_output_file, 'w', encoding='utf-8') as f:
            f.write(result_text)
        print(f"\n结果已保存到文件: {default_output_file}")
    
    # 输出到控制台
    print("\n" + result_text)
    
    return result_text


def calculate_similarity(str1: str, str2: str) -> float:
    """
    计算两个字符串的相似度（0.0-1.0，1.0表示完全相同）
    
    Args:
        str1: 第一个字符串
        str2: 第二个字符串
        
    Returns:
        float: 相似度值（0.0-1.0）
    """
    return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()


def normalize_line_name(name: str) -> str:
    """
    标准化线路名称，用于比对
    去掉常见的修饰词：路、线、上行、下行、左环、右环等
    
    Args:
        name: 原始线路名称
        
    Returns:
        str: 标准化后的名称
    """
    normalized = name.strip()
    
    # 去掉"路"、"线"等后缀
    normalized = re.sub(r'[路线]$', '', normalized)
    normalized = normalized.strip()
    
    return normalized


def find_best_match(target: str, candidates: List[str], threshold: float = 0.8) -> Tuple[Optional[str], float]:
    """
    在候选列表中找到与目标字符串最相似的匹配项
    使用标准化后的名称进行比对
    
    Args:
        target: 目标字符串
        candidates: 候选字符串列表
        threshold: 相似度阈值，低于此值不认为匹配
        
    Returns:
        Tuple[Optional[str], float]: (匹配的字符串, 相似度) 如果没有匹配返回 (None, 0.0)
    """
    best_match = None
    best_similarity = 0.0
    
    # 标准化目标字符串
    target_normalized = normalize_line_name(target)
    
    for candidate in candidates:
        # 标准化候选字符串
        candidate_normalized = normalize_line_name(candidate)
        
        # 先尝试精确匹配（标准化后）
        if target_normalized == candidate_normalized:
            return candidate, 1.0
        
        # 再尝试相似度匹配
        similarity = calculate_similarity(target_normalized, candidate_normalized)
        if similarity > best_similarity:
            best_similarity = similarity
            best_match = candidate
    
    if best_similarity >= threshold:
        return best_match, best_similarity
    else:
        return None, best_similarity


def compare_excel_line_names(excel_path_a: str, excel_path_b: str, similarity_threshold: float = 0.8, output_file: Optional[str] = None) -> str:
    """
    对比两个Excel文件中的线路名称，找出差异
    
    Args:
        excel_path_a: 第一个Excel文件路径（线路表.xlsx，从数据中提取线路名称）
        excel_path_b: 第二个Excel文件路径（线路站级表.xlsx，从Sheet名称提取线路名称）
        similarity_threshold: 相似度阈值，默认0.8（80%相似度以上认为是同一线路）
        output_file: 输出文件路径，如果为None则自动生成
        
    Returns:
        str: 对比结果文本
    """
    print("=" * 80)
    print("开始对比两个Excel文件的线路名称")
    print("=" * 80)
    
    # 获取A表的线路名称（从Excel数据中提取）
    print(f"\n正在解析文件A: {excel_path_a}")
    try:
        line_names_a = get_line_names(excel_path_a)
        print(f"文件A共找到 {len(line_names_a)} 个不同的线路名称")
    except Exception as e:
        raise Exception(f"解析文件A失败: {str(e)}")
    
    # 获取B表的线路名称（从Sheet名称中提取）
    print(f"\n正在解析文件B: {excel_path_b}")
    try:
        line_names_b_original = get_sheet_names_from_excel(excel_path_b)
        print(f"线路站级表共找到 {len(line_names_b_original)} 个Sheet（线路名称）")
    except Exception as e:
        raise Exception(f"解析线路站级表失败: {str(e)}")
    
    # 处理线路站级表的线路名称：去掉DJ_和GD_前缀、上/下行标记、括号内容等
    # 同时创建原始名称和处理后名称的映射
    line_names_b_processed = []  # 用于比对的处理后名称列表
    b_name_mapping = {}  # 处理后名称 -> 原始名称列表的映射
    for original_name in line_names_b_original:
        processed_name = original_name
        
        # 1. 去掉DJ_和GD_前缀
        if processed_name.startswith('DJ_'):
            processed_name = processed_name[3:]  # 去掉前3个字符'DJ_'
        elif processed_name.startswith('GD_'):
            processed_name = processed_name[3:]  # 去掉前3个字符'GD_'
        
        # 2. 去掉所有括号及其内容，包括 (2)、(左环)、(右环)、(上行)、(下行)、(学生线) 等
        processed_name = re.sub(r'[（(][^）)]*[）)]', '', processed_name)
        processed_name = processed_name.strip()
        
        # 3. 去掉上/下行标记（在去掉括号后，可能还有残留的"上行"、"下行"等）
        processed_name = re.sub(r'[上下]行[线]?', '', processed_name, flags=re.IGNORECASE)
        processed_name = processed_name.strip()
        
        # 4. 去掉左右环标记
        processed_name = re.sub(r'[左右]环', '', processed_name, flags=re.IGNORECASE)
        processed_name = processed_name.strip()
        
        line_names_b_processed.append(processed_name)
        # 使用列表保存所有映射到同一个处理后名称的原始名称
        if processed_name not in b_name_mapping:
            b_name_mapping[processed_name] = []
        b_name_mapping[processed_name].append(original_name)
    
    # 准备输出文本
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append(f"Excel线路名称对比结果")
    output_lines.append(f"对比时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output_lines.append(f"线路信息表: {excel_path_a}")
    output_lines.append(f"线路站级表: {excel_path_b}")
    output_lines.append(f"相似度阈值: {similarity_threshold}")
    output_lines.append(f"文件A线路总数: {len(line_names_a)}")
    output_lines.append(f"文件B线路总数: {len(line_names_b_original)}")
    output_lines.append("说明: B表线路名称已去掉DJ_和GD_前缀进行比对")
    output_lines.append("=" * 80)
    output_lines.append("")
    
    # 使用集合来记录已匹配的线路（使用原始名称）
    matched_b_original = set()
    
    # 找出A表有B表没有的线路
    output_lines.append("【A表有，B表没有的线路】")
    output_lines.append("-" * 80)
    only_in_a = []
    
    for line_a in line_names_a:
        # 使用处理后的名称列表进行比对
        best_match_processed, similarity = find_best_match(line_a, line_names_b_processed, similarity_threshold)
        if best_match_processed is None:
            only_in_a.append(line_a)
        else:
            # 找到匹配后，使用映射获取原始名称（可能有多个原始名称对应同一个处理后名称）
            original_names = b_name_mapping[best_match_processed]
            for orig_name in original_names:
                matched_b_original.add(orig_name)
    
    if only_in_a:
        output_lines.append(f"共 {len(only_in_a)} 条线路：")
        for idx, line_name in enumerate(only_in_a, 1):
            output_lines.append(f"  {idx}. {line_name}")
    else:
        output_lines.append("无")
    
    output_lines.append("")
    
    # 找出线路站级表有、线路信息表没有的线路（使用原始名称）
    output_lines.append("【线路站级表有，线路信息表没有的线路】")
    output_lines.append("-" * 80)
    only_in_b = [line_b for line_b in line_names_b_original if line_b not in matched_b_original]
    
    if only_in_b:
        output_lines.append(f"共 {len(only_in_b)} 条线路：")
        for idx, line_name in enumerate(only_in_b, 1):
            output_lines.append(f"  {idx}. {line_name}")
    else:
        output_lines.append("无")
    
    output_lines.append("")
    
    # 找出匹配的线路（显示相似度）
    output_lines.append("【匹配的线路（相似度信息）】")
    output_lines.append("-" * 80)
    matched_pairs = []
    
    for line_a in line_names_a:
        # 使用处理后的名称列表进行比对
        best_match_processed, similarity = find_best_match(line_a, line_names_b_processed, similarity_threshold)
        if best_match_processed is not None:
            # 使用映射获取原始名称用于显示（如果有多个，只取第一个）
            original_names = b_name_mapping[best_match_processed]
            best_match_original = original_names[0] if original_names else best_match_processed
            matched_pairs.append((line_a, best_match_original, similarity))
    
    if matched_pairs:
        output_lines.append(f"共 {len(matched_pairs)} 对匹配线路：")
        for idx, (line_a, line_b, sim) in enumerate(matched_pairs, 1):
            output_lines.append(f"  {idx}. 线路信息表: {line_a} <-> 线路站级表: {line_b} (相似度: {sim:.2%})")
    else:
        output_lines.append("无完全匹配的线路")
    
    output_lines.append("")
    
    # 添加统计信息
    output_lines.append("=" * 80)
    output_lines.append("统计信息")
    output_lines.append("=" * 80)
    output_lines.append(f"线路信息表线路总数: {len(line_names_a)}")
    output_lines.append(f"线路站级表线路总数: {len(line_names_b_original)}")
    output_lines.append(f"线路信息表独有线路数: {len(only_in_a)}")
    output_lines.append(f"线路站级表独有线路数: {len(only_in_b)}")
    output_lines.append(f"匹配的线路对数: {len(matched_pairs)}")
    output_lines.append("=" * 80)
    
    # 生成完整文本
    result_text = "\n".join(output_lines)
    
    # 输出到文件
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result_text)
        print(f"\n结果已保存到文件: {output_file}")
    else:
        # 如果没有指定输出文件，生成默认文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_output_file = os.path.join(
            os.path.dirname(excel_path_a),
            f'Excel线路名称对比结果_{timestamp}.txt'
        )
        with open(default_output_file, 'w', encoding='utf-8') as f:
            f.write(result_text)
        print(f"\n结果已保存到文件: {default_output_file}")
    
    # 输出到控制台
    print("\n" + result_text)
    
    return result_text


if __name__ == "__main__":
    print("=" * 60)
    print("公交线路高德地图API查询工具")
    print("=" * 60)
    print("请选择解析方式：")
    print("  1. 基于Excel数据查询（解析线路表.xlsx中的线路名称）")
    print("  2. 基于Sheet名称查询（解析线路站级表.xlsx中的Sheet名称）")
    print("  3. 对比两个Excel文件的线路名称（找出差异）")
    print("=" * 60)
    
    while True:
        choice = input("请输入选项 (1、2 或 3): ").strip()
        if choice == '1':
            # 第一个服务：基于Excel数据查询
            excel_path = r"Z:\Work\ACode\太仓线网\AdminBackend\Excel\线路表.xlsx"
            try:
                print(f"\n开始执行：基于Excel数据查询")
                query_bus_lines_from_gaode(
                    excel_path=excel_path,
                    city=AMAP_CITY_CODE,
                    output_file=None  # 使用默认文件名
                )
            except Exception as e:
                print(f"执行失败: {str(e)}")
                import traceback
                traceback.print_exc()
            break
        elif choice == '2':
            # 第二个服务：基于Sheet名称查询
            excel_path = r"Z:\Work\ACode\太仓线网\AdminBackend\Excel\线路站级表.xlsx"
            try:
                print(f"\n开始执行：基于Sheet名称查询")
                query_bus_lines_from_sheet_names(
                    excel_path=excel_path,
                    city=AMAP_CITY_CODE,
                    output_file=None  # 使用默认文件名
                )
            except Exception as e:
                print(f"执行失败: {str(e)}")
                import traceback
                traceback.print_exc()
            break
        elif choice == '3':
            # 第三个服务：对比两个Excel文件的线路名称
            excel_path_a = r"Z:\Work\ACode\太仓线网\AdminBackend\Excel\线路表.xlsx"
            excel_path_b = r"Z:\Work\ACode\太仓线网\AdminBackend\Excel\线路站级表.xlsx"
            try:
                print(f"\n开始执行：对比两个Excel文件的线路名称")
                compare_excel_line_names(
                    excel_path_a=excel_path_a,
                    excel_path_b=excel_path_b,
                    similarity_threshold=0.8,  # 80%相似度阈值
                    output_file=None  # 使用默认文件名
                )
            except Exception as e:
                print(f"执行失败: {str(e)}")
                import traceback
                traceback.print_exc()
            break
        else:
            print("无效的选项，请输入 1、2 或 3")

