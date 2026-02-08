# -*- coding: utf-8 -*-

"""
工具类使用示例
展示如何使用重新组织后的工具类模块

@author: 王晨
@Created on: 2024/12/19
@Remark: 工具类使用示例，展示新的模块结构
"""

# 方式1：直接导入geo模块
from dvadmin_twodev.utils.geo import GeoCalculator, CoordConverter, GridCalculator

# 方式2：通过utils模块导入
from dvadmin_twodev.utils import geo

def example_usage():
    """使用示例"""
    print("=== 地图几何计算工具类使用示例 ===")
    
    # 使用方式1：直接导入的类
    point1 = (121.123456, 31.234567)
    point2 = (121.133456, 31.244567)
    
    distance = GeoCalculator.calculate_distance_haversine(point1, point2)
    print(f"距离计算: {distance:.2f} 米")
    
    # 使用方式2：通过模块导入
    center = geo.GridCalculator.calculate_grid_center(point1, point2)
    print(f"中心点: {center}")
    
    # 坐标系转换
    wgs84_coord = CoordConverter.tencent_to_wgs84(point1)
    print(f"WGS84坐标: {wgs84_coord}")
    
    print("所有功能正常工作！")

if __name__ == "__main__":
    example_usage()
