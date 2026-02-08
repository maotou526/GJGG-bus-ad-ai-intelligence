# -*- coding: utf-8 -*-

"""
地图几何计算工具类使用示例
展示如何使用GeoCalculator、CoordConverter、GridCalculator等工具类

@author: 太仓线网开发团队
@Created on: 2024/12/19
@Remark: 使用示例和测试用例
"""

from .geo_utils import GeoCalculator, CoordConverter, GridCalculator


def example_basic_calculations():
    """
    基础几何计算示例
    """
    print("=== 基础几何计算示例 ===")
    
    # 定义两个点坐标（腾讯坐标系）
    point1 = (121.123456, 31.234567)  # 经度, 纬度
    point2 = (121.133456, 31.244567)
    
    # 计算距离
    distance_haversine = GeoCalculator.calculate_distance_haversine(point1, point2)
    distance_vincenty = GeoCalculator.calculate_distance_vincenty(point1, point2)
    
    print(f"点1: {point1}")
    print(f"点2: {point2}")
    print(f"Haversine距离: {distance_haversine:.2f} 米")
    print(f"Vincenty距离: {distance_vincenty:.2f} 米")
    
    # 计算方位角
    bearing = GeoCalculator.calculate_bearing(point1, point2)
    print(f"方位角: {bearing:.2f} 度")
    
    # 计算中点
    midpoint = GeoCalculator.calculate_midpoint(point1, point2)
    print(f"中点: {midpoint}")
    
    print()


def example_polygon_operations():
    """
    多边形操作示例
    """
    print("=== 多边形操作示例 ===")
    
    # 定义一个矩形多边形
    polygon = [
        (121.1, 31.1),  # 左下角
        (121.2, 31.1),  # 右下角
        (121.2, 31.2),  # 右上角
        (121.1, 31.2)   # 左上角
    ]
    
    # 测试点
    test_point_inside = (121.15, 31.15)  # 在多边形内
    test_point_outside = (121.25, 31.25)  # 在多边形外
    
    # 判断点是否在多边形内
    is_inside1 = GeoCalculator.is_point_in_polygon(test_point_inside, polygon)
    is_inside2 = GeoCalculator.is_point_in_polygon(test_point_outside, polygon)
    
    print(f"多边形顶点: {polygon}")
    print(f"测试点1 {test_point_inside} 是否在多边形内: {is_inside1}")
    print(f"测试点2 {test_point_outside} 是否在多边形内: {is_inside2}")
    
    # 计算多边形面积
    area = GeoCalculator.calculate_polygon_area(polygon)
    print(f"多边形面积: {area:.2f} 平方米")
    
    print()


def example_coordinate_conversion():
    """
    坐标系转换示例
    """
    print("=== 坐标系转换示例 ===")
    
    # 腾讯坐标系坐标
    tencent_coord = (121.123456, 31.234567)
    
    # 转换为WGS84坐标系
    wgs84_coord = CoordConverter.tencent_to_wgs84(tencent_coord)
    
    # 再转换回腾讯坐标系
    tencent_coord_back = CoordConverter.wgs84_to_tencent(wgs84_coord)
    
    print(f"腾讯坐标系: {tencent_coord}")
    print(f"WGS84坐标系: {wgs84_coord}")
    print(f"转换回腾讯坐标系: {tencent_coord_back}")
    
    print()


def example_grid_calculations():
    """
    网格计算示例
    """
    print("=== 网格计算示例 ===")
    
    # 定义网格边界
    bottom_left = (121.1, 31.1)
    top_right = (121.2, 31.2)
    
    # 计算网格中心点
    center = GridCalculator.calculate_grid_center(bottom_left, top_right)
    
    # 计算网格面积
    area = GridCalculator.calculate_grid_area(bottom_left, top_right)
    
    # 测试点是否在网格内
    test_point = (121.15, 31.15)
    is_in_grid = GridCalculator.is_point_in_grid(test_point, bottom_left, top_right)
    
    print(f"网格左下角: {bottom_left}")
    print(f"网格右上角: {top_right}")
    print(f"网格中心点: {center}")
    print(f"网格面积: {area:.2f} 平方米")
    print(f"测试点 {test_point} 是否在网格内: {is_in_grid}")
    
    print()


def example_coordinate_parsing():
    """
    坐标解析示例
    """
    print("=== 坐标解析示例 ===")
    
    # 测试不同的坐标字符串格式
    coord_strings = [
        "121.123456,31.234567",
        "121.123456, 31.234567",
        "121.123456 31.234567",
        "121.123456,31.234567,0",  # 带高程
        "invalid_coord"
    ]
    
    for coord_str in coord_strings:
        parsed = GeoCalculator.parse_coord_string(coord_str)
        if parsed:
            formatted = GeoCalculator.format_coord_string(parsed)
            is_valid = GeoCalculator.validate_coord_range(parsed)
            print(f"'{coord_str}' -> {parsed} -> '{formatted}' (有效: {is_valid})")
        else:
            print(f"'{coord_str}' -> 解析失败")
    
    print()


def example_real_world_usage():
    """
    实际使用场景示例
    """
    print("=== 实际使用场景示例 ===")
    
    # 模拟太仓线网项目中的实际使用场景
    
    # 1. 计算两个公交站点间的距离
    station1 = (121.123456, 31.234567)  # 站点1
    station2 = (121.133456, 31.244567)  # 站点2
    
    distance = GeoCalculator.calculate_distance_haversine(station1, station2)
    print(f"公交站点间距离: {distance:.2f} 米")
    
    # 2. 判断用户位置是否在某个网格内
    user_location = (121.15, 31.15)
    grid_bottom_left = (121.1, 31.1)
    grid_top_right = (121.2, 31.2)
    
    is_in_grid = GridCalculator.is_point_in_grid(user_location, grid_bottom_left, grid_top_right)
    print(f"用户位置 {user_location} 是否在网格内: {is_in_grid}")
    
    # 3. 计算网格的职住人口密度
    grid_area = GridCalculator.calculate_grid_area(grid_bottom_left, grid_top_right)
    work_population = 1000  # 工作人数
    reside_population = 800  # 居住人数
    
    work_density = work_population / (grid_area / 1000000)  # 每平方km工作人数
    reside_density = reside_population / (grid_area / 1000000)  # 每平方km居住人数
    
    print(f"网格面积: {grid_area:.2f} 平方米")
    print(f"工作人口密度: {work_density:.2f} 人/平方km")
    print(f"居住人口密度: {reside_density:.2f} 人/平方km")
    
    print()


if __name__ == "__main__":
    """
    运行所有示例
    """
    print("地图几何计算工具类使用示例")
    print("=" * 50)
    
    example_basic_calculations()
    example_polygon_operations()
    example_coordinate_conversion()
    example_grid_calculations()
    example_coordinate_parsing()
    example_real_world_usage()
    
    print("所有示例运行完成！")
