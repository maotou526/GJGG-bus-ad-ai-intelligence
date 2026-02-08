# -*- coding: utf-8 -*-

"""
地图几何计算工具类测试文件
用于验证工具类的功能正确性

@author: 太仓线网开发团队
@Created on: 2024/12/19
@Remark: 单元测试和功能验证
"""

import unittest
from .geo_utils import GeoCalculator, CoordConverter, GridCalculator


class TestGeoCalculator(unittest.TestCase):
    """
    地图几何计算工具类测试
    """
    
    def setUp(self):
        """测试前准备"""
        # 定义测试用的坐标点
        self.point1 = (121.123456, 31.234567)
        self.point2 = (121.133456, 31.244567)
        self.point3 = (121.143456, 31.254567)
        
        # 定义测试用的多边形（矩形）
        self.rectangle = [
            (121.1, 31.1),  # 左下角
            (121.2, 31.1),  # 右下角
            (121.2, 31.2),  # 右上角
            (121.1, 31.2)   # 左上角
        ]
    
    def test_distance_calculation(self):
        """测试距离计算"""
        # 测试Haversine距离计算
        distance = GeoCalculator.calculate_distance_haversine(self.point1, self.point2)
        self.assertGreater(distance, 0, "距离应该大于0")
        self.assertLess(distance, 10000, "距离应该在合理范围内")
        
        # 测试Vincenty距离计算
        distance_vincenty = GeoCalculator.calculate_distance_vincenty(self.point1, self.point2)
        self.assertGreater(distance_vincenty, 0, "Vincenty距离应该大于0")
        
        # 相同点的距离应该为0
        same_point_distance = GeoCalculator.calculate_distance_haversine(self.point1, self.point1)
        self.assertEqual(same_point_distance, 0, "相同点的距离应该为0")
    
    def test_point_in_polygon(self):
        """测试点在多边形内判断"""
        # 测试在多边形内的点
        point_inside = (121.15, 31.15)
        is_inside = GeoCalculator.is_point_in_polygon(point_inside, self.rectangle)
        self.assertTrue(is_inside, "点应该在多边形内")
        
        # 测试在多边形外的点
        point_outside = (121.25, 31.25)
        is_outside = GeoCalculator.is_point_in_polygon(point_outside, self.rectangle)
        self.assertFalse(is_outside, "点应该在多边形外")
    
    def test_point_in_rectangle(self):
        """测试点在矩形内判断"""
        bottom_left = (121.1, 31.1)
        top_right = (121.2, 31.2)
        
        # 测试在矩形内的点
        point_inside = (121.15, 31.15)
        is_inside = GeoCalculator.is_point_in_rectangle(point_inside, bottom_left, top_right)
        self.assertTrue(is_inside, "点应该在矩形内")
        
        # 测试在矩形外的点
        point_outside = (121.25, 31.25)
        is_outside = GeoCalculator.is_point_in_rectangle(point_outside, bottom_left, top_right)
        self.assertFalse(is_outside, "点应该在矩形外")
    
    def test_polygon_area(self):
        """测试多边形面积计算"""
        area = GeoCalculator.calculate_polygon_area(self.rectangle)
        self.assertGreater(area, 0, "面积应该大于0")
        
        # 空多边形的面积应该为0
        empty_polygon = []
        empty_area = GeoCalculator.calculate_polygon_area(empty_polygon)
        self.assertEqual(empty_area, 0, "空多边形的面积应该为0")
    
    def test_bearing_calculation(self):
        """测试方位角计算"""
        bearing = GeoCalculator.calculate_bearing(self.point1, self.point2)
        self.assertGreaterEqual(bearing, 0, "方位角应该大于等于0")
        self.assertLess(bearing, 360, "方位角应该小于360度")
        
        # 相同点的方位角应该为0
        same_bearing = GeoCalculator.calculate_bearing(self.point1, self.point1)
        self.assertEqual(same_bearing, 0, "相同点的方位角应该为0")
    
    def test_midpoint_calculation(self):
        """测试中点计算"""
        midpoint = GeoCalculator.calculate_midpoint(self.point1, self.point2)
        expected_lng = (self.point1[0] + self.point2[0]) / 2
        expected_lat = (self.point1[1] + self.point2[1]) / 2
        
        self.assertAlmostEqual(midpoint[0], expected_lng, places=6, msg="中点经度计算错误")
        self.assertAlmostEqual(midpoint[1], expected_lat, places=6, msg="中点纬度计算错误")
    
    def test_coordinate_parsing(self):
        """测试坐标解析"""
        # 测试有效的坐标字符串
        coord_str = "121.123456,31.234567"
        parsed = GeoCalculator.parse_coord_string(coord_str)
        self.assertIsNotNone(parsed, "应该能解析有效的坐标字符串")
        self.assertEqual(parsed, (121.123456, 31.234567), "解析结果应该正确")
        
        # 测试无效的坐标字符串
        invalid_str = "invalid_coord"
        invalid_parsed = GeoCalculator.parse_coord_string(invalid_str)
        self.assertIsNone(invalid_parsed, "无效坐标字符串应该返回None")
    
    def test_coordinate_formatting(self):
        """测试坐标格式化"""
        coord = (121.123456, 31.234567)
        formatted = GeoCalculator.format_coord_string(coord, precision=4)
        expected = "121.1235,31.2346"
        self.assertEqual(formatted, expected, "坐标格式化结果应该正确")
    
    def test_coordinate_validation(self):
        """测试坐标验证"""
        # 测试有效坐标
        valid_coord = (121.123456, 31.234567)
        is_valid = GeoCalculator.validate_coord_range(valid_coord)
        self.assertTrue(is_valid, "有效坐标应该通过验证")
        
        # 测试无效经度
        invalid_lng = (181.0, 31.234567)
        is_invalid_lng = GeoCalculator.validate_coord_range(invalid_lng)
        self.assertFalse(is_invalid_lng, "无效经度应该不通过验证")
        
        # 测试无效纬度
        invalid_lat = (121.123456, 91.0)
        is_invalid_lat = GeoCalculator.validate_coord_range(invalid_lat)
        self.assertFalse(is_invalid_lat, "无效纬度应该不通过验证")


class TestCoordConverter(unittest.TestCase):
    """
    坐标系转换工具类测试
    """
    
    def test_tencent_to_wgs84(self):
        """测试腾讯坐标系转WGS84坐标系"""
        tencent_coord = (121.123456, 31.234567)
        wgs84_coord = CoordConverter.tencent_to_wgs84(tencent_coord)
        
        # 转换后的坐标应该与原始坐标不同
        self.assertNotEqual(tencent_coord, wgs84_coord, "转换后的坐标应该与原始坐标不同")
        
        # 转换后的坐标应该在合理范围内
        self.assertTrue(GeoCalculator.validate_coord_range(wgs84_coord), "转换后的坐标应该有效")
    
    def test_wgs84_to_tencent(self):
        """测试WGS84坐标系转腾讯坐标系"""
        wgs84_coord = (121.123456, 31.234567)
        tencent_coord = CoordConverter.wgs84_to_tencent(wgs84_coord)
        
        # 转换后的坐标应该与原始坐标不同
        self.assertNotEqual(wgs84_coord, tencent_coord, "转换后的坐标应该与原始坐标不同")
        
        # 转换后的坐标应该在合理范围内
        self.assertTrue(GeoCalculator.validate_coord_range(tencent_coord), "转换后的坐标应该有效")
    
    def test_coordinate_conversion_roundtrip(self):
        """测试坐标系转换的往返转换"""
        original_tencent = (121.123456, 31.234567)
        
        # 腾讯 -> WGS84 -> 腾讯
        wgs84 = CoordConverter.tencent_to_wgs84(original_tencent)
        back_to_tencent = CoordConverter.wgs84_to_tencent(wgs84)
        
        # 往返转换后应该接近原始坐标（允许小的误差）
        self.assertAlmostEqual(original_tencent[0], back_to_tencent[0], places=6, 
                              msg="往返转换后经度应该接近原始值")
        self.assertAlmostEqual(original_tencent[1], back_to_tencent[1], places=6, 
                              msg="往返转换后纬度应该接近原始值")


class TestGridCalculator(unittest.TestCase):
    """
    网格计算工具类测试
    """
    
    def setUp(self):
        """测试前准备"""
        self.bottom_left = (121.1, 31.1)
        self.top_right = (121.2, 31.2)
    
    def test_grid_center_calculation(self):
        """测试网格中心点计算"""
        center = GridCalculator.calculate_grid_center(self.bottom_left, self.top_right)
        expected_center = (121.15, 31.15)
        
        self.assertAlmostEqual(center[0], expected_center[0], places=6, 
                              msg="网格中心点经度计算错误")
        self.assertAlmostEqual(center[1], expected_center[1], places=6, 
                              msg="网格中心点纬度计算错误")
    
    def test_grid_area_calculation(self):
        """测试网格面积计算"""
        area = GridCalculator.calculate_grid_area(self.bottom_left, self.top_right)
        self.assertGreater(area, 0, "网格面积应该大于0")
    
    def test_point_in_grid(self):
        """测试点是否在网格内"""
        # 测试在网格内的点
        point_inside = (121.15, 31.15)
        is_inside = GridCalculator.is_point_in_grid(point_inside, self.bottom_left, self.top_right)
        self.assertTrue(is_inside, "点应该在网格内")
        
        # 测试在网格外的点
        point_outside = (121.25, 31.25)
        is_outside = GridCalculator.is_point_in_grid(point_outside, self.bottom_left, self.top_right)
        self.assertFalse(is_outside, "点应该在网格外")


if __name__ == '__main__':
    """
    运行测试
    """
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_suite.addTest(unittest.makeSuite(TestGeoCalculator))
    test_suite.addTest(unittest.makeSuite(TestCoordConverter))
    test_suite.addTest(unittest.makeSuite(TestGridCalculator))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出测试结果
    print(f"\n测试结果: {result.testsRun} 个测试")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)} 个")
    print(f"失败: {len(result.failures)} 个")
    print(f"错误: {len(result.errors)} 个")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
