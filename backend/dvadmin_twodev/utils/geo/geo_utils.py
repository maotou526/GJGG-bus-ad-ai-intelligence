# -*- coding: utf-8 -*-

"""
地图几何计算工具类
提供常用的地图坐标计算、几何运算等功能
适用于太仓线网项目的地图数据处理需求

@author: 王晨
@contact: 
@Created on: 2024/12/19
@Remark: 地图几何计算工具类，包含坐标转换、距离计算、几何运算等功能
"""

import math
from typing import Tuple, List, Optional, Union
from decimal import Decimal, getcontext

# 设置高精度计算上下文（用于需要极高精度的计算场景）
# 注意：当前代码主要使用float类型，此设置为预留的高精度计算能力
getcontext().prec = 28


class GeoCalculator:
    """
    地图几何计算工具类
    提供坐标转换、距离计算、几何运算等功能
    支持腾讯坐标系和WGS84坐标系
    """
    
    # 地球半径常量（米）
    EARTH_RADIUS = 6371000
    
    # 腾讯坐标系与WGS84坐标系的转换参数
    # 这些参数需要根据实际使用的地图服务商进行调整
    COORD_OFFSET_X = 0.0065  # 经度偏移量
    COORD_OFFSET_Y = 0.0060  # 纬度偏移量
    
    @staticmethod
    def densify_polyline(
        coord_str: str,
        interval_meter: float,
        separator: str = ';',
        precision: int = 6,
    ) -> str:
        """
        对线路经纬度轨迹进行补点（加密折线）
        
        轨迹字符串格式示例：
            "121.20029657101945,31.480206405199024;121.20046184337986,31.48031464668348"
        
        Args:
            coord_str: 原始轨迹字符串，lng,lat 使用逗号分隔，点与点之间使用分号分隔
            interval_meter: 补点间隔（米），大于0
            separator: 轨迹中点与点之间的分隔符，默认 ';'
            precision: 输出经纬度小数位数
        
        Returns:
            str: 补点后的轨迹字符串，格式同输入
        """
        from typing import List, Tuple  # 避免循环导入，仅在方法内使用

        # 入参校验
        if not coord_str or not coord_str.strip():
            return ''
        if interval_meter is None or interval_meter <= 0:
            # 间隔无效时直接返回原始轨迹
            return coord_str

        # 解析原始坐标串为点列表
        points: List[Tuple[float, float]] = GeoCalculator.parse_coords_string(coord_str, separator=separator)
        if len(points) < 2:
            # 少于两个点无法补点，直接返回
            return coord_str

        densified: List[Tuple[float, float]] = []

        for idx in range(len(points) - 1):
            p_start = points[idx]
            p_end = points[idx + 1]

            # 起点永远保留
            if idx == 0:
                densified.append(p_start)

            # 计算该段长度
            dist = GeoCalculator.calculate_distance_haversine(p_start, p_end)
            if dist <= interval_meter:
                # 段长小于等于间隔，不补点，直接加入终点（下轮起点会处理）
                densified.append(p_end)
                continue

            # 需要补点的数量（不包含两端点）
            # 例如 dist=250, interval=100 -> n = int(250/100)=2 -> 2个补点
            num_new = int(dist // interval_meter)
            if num_new <= 0:
                densified.append(p_end)
                continue

            lng1, lat1 = p_start
            lng2, lat2 = p_end

            # 线性插值（在经纬度空间近似为直线）
            for i in range(1, num_new + 1):
                t = (interval_meter * i) / dist
                # 防止浮点误差导致 t > 1
                if t >= 1:
                    break
                lng = lng1 + (lng2 - lng1) * t
                lat = lat1 + (lat2 - lat1) * t
                densified.append((lng, lat))

            # 段终点
            densified.append(p_end)

        # 去重：防止数值误差导致连续重复点
        cleaned: List[Tuple[float, float]] = []
        for pt in densified:
            if not cleaned:
                cleaned.append(pt)
                continue
            prev = cleaned[-1]
            if abs(prev[0] - pt[0]) < 1e-10 and abs(prev[1] - pt[1]) < 1e-10:
                continue
            cleaned.append(pt)

        # 格式化为字符串
        return GeoCalculator.format_coords_string(cleaned, separator=separator, precision=precision)
    
    @staticmethod
    def calculate_polyline_overlap(
        main_coord_str: str,
        vice_coord_str: str,
        sample_interval: float = 10.0,
        match_threshold: float = 15.0,
        separator: str = ';',
        precision: int = 6,
    ) -> Tuple[float, float, float, str]:
        """
        计算两条线路轨迹的复线情况
        
        结果包含：
        - 复线总长度（米）
        - 主线路复线率（复线长度 / 主线路总长度）
        - 副线路复线率（复线长度 / 副线路总长度）
        - 复线段轨迹字符串（多个复线段使用 '|' 分割，每段内部使用 ';' 分割坐标点）
        
        轨迹字符串格式示例：
            "121.2,31.48;121.21,31.49;..."
        
        算法思路（近似）：
        1. 先对两条轨迹按给定采样间隔进行加密（densify），得到更密集的点序列；
        2. 对主线路上的每一个采样点，查找是否存在一条副线路采样点在一定距离阈值内；
        3. 将相邻的“匹配点”合并为连续的复线段；
        4. 复线长度通过主线路采样点序列累积计算。
        
        Args:
            main_coord_str: 主线路轨迹字符串
            vice_coord_str: 副线路轨迹字符串
            sample_interval: 采样/补点间隔（米），用于加密轨迹
            match_threshold: 认为两条线重合的距离阈值（米）
            separator: 轨迹中点与点之间的分隔符，默认 ';'
            precision: 输出经纬度小数位数
        
        Returns:
            Tuple[float, float, float, str]:
                (repeat_length, main_repeat_rate, vice_repeat_rate, repeat_lon_lat_str)
        """
        # 基本校验
        if not main_coord_str or not main_coord_str.strip():
            return 0.0, 0.0, 0.0, ''
        if not vice_coord_str or not vice_coord_str.strip():
            return 0.0, 0.0, 0.0, ''
        if sample_interval <= 0:
            sample_interval = 10.0
        if match_threshold <= 0:
            match_threshold = 15.0

        # 解析原始轨迹，计算各自总长度
        main_points = GeoCalculator.parse_coords_string(main_coord_str, separator=separator)
        vice_points = GeoCalculator.parse_coords_string(vice_coord_str, separator=separator)

        if len(main_points) < 2 or len(vice_points) < 2:
            return 0.0, 0.0, 0.0, ''

        def _polyline_length(points: List[Tuple[float, float]]) -> float:
            total = 0.0
            for i in range(len(points) - 1):
                total += GeoCalculator.calculate_distance_haversine(points[i], points[i + 1])
            return total

        main_length = _polyline_length(main_points)
        vice_length = _polyline_length(vice_points)

        if main_length <= 0 or vice_length <= 0:
            return 0.0, 0.0, 0.0, ''

        # 对两条线路进行加密采样
        densified_main_str = GeoCalculator.densify_polyline(
            main_coord_str,
            interval_meter=sample_interval,
            separator=separator,
            precision=precision,
        )
        densified_vice_str = GeoCalculator.densify_polyline(
            vice_coord_str,
            interval_meter=sample_interval,
            separator=separator,
            precision=precision,
        )

        densified_main = GeoCalculator.parse_coords_string(densified_main_str, separator=separator)
        densified_vice = GeoCalculator.parse_coords_string(densified_vice_str, separator=separator)

        if len(densified_main) < 2 or len(densified_vice) < 2:
            return 0.0, 0.0, 0.0, ''

        # 对主线路上的采样点逐个判断是否与副线路“重合”
        overlap_flags: List[bool] = []
        for p_main in densified_main:
            has_match = False
            for p_vice in densified_vice:
                d = GeoCalculator.calculate_distance_haversine(p_main, p_vice)
                if d <= match_threshold:
                    has_match = True
                    break
            overlap_flags.append(has_match)

        # 根据 overlap_flags 切分连续的复线段
        overlap_segments: List[List[Tuple[float, float]]] = []
        current_seg: List[Tuple[float, float]] = []

        for idx, flag in enumerate(overlap_flags):
            pt = densified_main[idx]
            if flag:
                # 落在复线范围内
                if not current_seg:
                    current_seg.append(pt)
                else:
                    current_seg.append(pt)
            else:
                # 离开复线，如果当前段有点则收尾
                if len(current_seg) >= 2:
                    overlap_segments.append(current_seg)
                current_seg = []

        # 末尾补充
        if len(current_seg) >= 2:
            overlap_segments.append(current_seg)

        if not overlap_segments:
            return 0.0, 0.0, 0.0, ''

        # 输出复线段轨迹字符串：各段用 '|' 分割
        segment_str_list: List[str] = []
        for seg in overlap_segments:
            seg_str = GeoCalculator.format_coords_string(seg, separator=separator, precision=precision)
            if seg_str:
                segment_str_list.append(seg_str)

        repeat_lon_lat_str = '|'.join(segment_str_list)

        # 根据 | 分割复线轨迹，计算每一段的长度并累加
        repeat_length = 0.0
        if repeat_lon_lat_str:
            # 按 | 分割多段轨迹
            segment_strs = repeat_lon_lat_str.split('|')
            for seg_str in segment_strs:
                seg_str = seg_str.strip()
                if not seg_str:
                    continue
                # 解析该段的坐标点
                seg_points = GeoCalculator.parse_coords_string(seg_str, separator=separator)
                if len(seg_points) >= 2:
                    # 计算该段的长度并累加
                    repeat_length += _polyline_length(seg_points)

        # 计算复线率
        main_repeat_rate = repeat_length / main_length if main_length > 0 else 0.0
        vice_repeat_rate = repeat_length / vice_length if vice_length > 0 else 0.0

        return repeat_length, float(main_repeat_rate), float(vice_repeat_rate), repeat_lon_lat_str
    
    @staticmethod
    def calculate_distance_haversine(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """
        使用Haversine公式计算两点间的距离（米）
        适用于短距离计算，精度较高
        
        Args:
            point1: 第一个点的坐标 (经度, 纬度)
            point2: 第二个点的坐标 (经度, 纬度)
            
        Returns:
            float: 两点间的距离（米）
        """
        lng1, lat1 = point1
        lng2, lat2 = point2
        
        # 将角度转换为弧度
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lng = math.radians(lng2 - lng1)
        
        # Haversine公式
        a = (math.sin(delta_lat / 2) ** 2 + 
             math.cos(lat1_rad) * math.cos(lat2_rad) * 
             math.sin(delta_lng / 2) ** 2)
        c = 2 * math.asin(math.sqrt(a))
        
        return GeoCalculator.EARTH_RADIUS * c
    
    @staticmethod
    def calculate_polyline_length(points: List[Tuple[float, float]]) -> float:
        """
        计算线路轨迹的总长度（米）
        通过累加所有相邻点之间的距离得到
        
        Args:
            points: 坐标点列表 [(经度, 纬度), ...]
            
        Returns:
            float: 线路总长度（米）
            
        Example:
            >>> points = [(121.1, 31.4), (121.2, 31.5), (121.3, 31.6)]
            >>> length = GeoCalculator.calculate_polyline_length(points)
            >>> print(f"线路长度: {length:.2f} 米")
        """
        if not points or len(points) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(len(points) - 1):
            total_length += GeoCalculator.calculate_distance_haversine(
                points[i], points[i + 1]
            )
        
        return total_length
    
    @staticmethod
    def calculate_max_distance_in_polyline(points: List[Tuple[float, float]]) -> float:
        """
        计算线路轨迹上最远两点间的距离（米）
        用于环线的非直线系数计算
        
        Args:
            points: 坐标点列表 [(经度, 纬度), ...]
            
        Returns:
            float: 最远两点间的距离（米）
            
        Example:
            >>> points = [(121.1, 31.4), (121.2, 31.5), (121.3, 31.6)]
            >>> max_dist = GeoCalculator.calculate_max_distance_in_polyline(points)
            >>> print(f"最远距离: {max_dist:.2f} 米")
        """
        if not points or len(points) < 2:
            return 0.0
        
        max_distance = 0.0
        # 遍历所有点对，找出距离最远的
        for i in range(len(points)):
            for j in range(i + 1, len(points)):
                distance = GeoCalculator.calculate_distance_haversine(
                    points[i], points[j]
                )
                if distance > max_distance:
                    max_distance = distance
        
        return max_distance
    
    @staticmethod
    def calculate_distance_vincenty(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """
        使用Vincenty公式计算两点间的距离（米）
        适用于长距离计算，精度更高
        
        Args:
            point1: 第一个点的坐标 (经度, 纬度)
            point2: 第二个点的坐标 (经度, 纬度)
            
        Returns:
            float: 两点间的距离（米）
        """
        lng1, lat1 = point1
        lng2, lat2 = point2
        
        # 椭球参数（WGS84）
        a = 6378137.0  # 长半轴
        f = 1 / 298.257223563  # 扁率
        b = (1 - f) * a  # 短半轴
        
        # 转换为弧度
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lng = math.radians(lng2 - lng1)
        
        # 计算辅助量
        U1 = math.atan((1 - f) * math.tan(lat1_rad))
        U2 = math.atan((1 - f) * math.tan(lat2_rad))
        sin_U1 = math.sin(U1)
        cos_U1 = math.cos(U1)
        sin_U2 = math.sin(U2)
        cos_U2 = math.cos(U2)
        
        # 迭代计算
        L = delta_lng
        lambda_p = L
        iteration_limit = 100
        
        for _ in range(iteration_limit):
            sin_lambda = math.sin(lambda_p)
            cos_lambda = math.cos(lambda_p)
            sin_sigma = math.sqrt(
                (cos_U2 * sin_lambda) ** 2 + 
                (cos_U1 * sin_U2 - sin_U1 * cos_U2 * cos_lambda) ** 2
            )
            
            if sin_sigma == 0:
                return 0.0  # 重合点
            
            cos_sigma = sin_U1 * sin_U2 + cos_U1 * cos_U2 * cos_lambda
            sigma = math.atan2(sin_sigma, cos_sigma)
            sin_alpha = cos_U1 * cos_U2 * sin_lambda / sin_sigma
            cos2_alpha = 1 - sin_alpha ** 2
            
            if cos2_alpha == 0:
                cos_2sigma_m = 0  # 赤道线
            else:
                cos_2sigma_m = cos_sigma - 2 * sin_U1 * sin_U2 / cos2_alpha
            
            C = f / 16 * cos2_alpha * (4 + f * (4 - 3 * cos2_alpha))
            lambda_new = L + (1 - C) * f * sin_alpha * (
                sigma + C * sin_sigma * (
                    cos_2sigma_m + C * cos_sigma * (-1 + 2 * cos_2sigma_m ** 2)
                )
            )
            
            if abs(lambda_new - lambda_p) < 1e-12:
                break
            lambda_p = lambda_new
        
        # 计算最终距离
        u2 = cos2_alpha * (a ** 2 - b ** 2) / (b ** 2)
        A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
        B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))
        delta_sigma = B * sin_sigma * (
            cos_2sigma_m + B / 4 * (
                cos_sigma * (-1 + 2 * cos_2sigma_m ** 2) -
                B / 6 * cos_2sigma_m * (-3 + 4 * sin_sigma ** 2) * (-3 + 4 * cos_2sigma_m ** 2)
            )
        )
        
        return b * A * (sigma - delta_sigma)
    
    @staticmethod
    def is_point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
        """
        判断点是否在多边形内
        使用射线法（Ray Casting Algorithm）
        
        Args:
            point: 要判断的点坐标 (经度, 纬度)
            polygon: 多边形顶点坐标列表 [(经度, 纬度), ...]
            
        Returns:
            bool: True表示点在多边形内，False表示在外部
        """
        if len(polygon) < 3:
            return False
        
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    @staticmethod
    def is_point_in_rectangle(point: Tuple[float, float], 
                            bottom_left: Tuple[float, float], 
                            top_right: Tuple[float, float]) -> bool:
        """
        判断点是否在矩形内
        
        Args:
            point: 要判断的点坐标 (经度, 纬度)
            bottom_left: 矩形左下角坐标 (经度, 纬度)
            top_right: 矩形右上角坐标 (经度, 纬度)
            
        Returns:
            bool: True表示点在矩形内，False表示在外部
        """
        x, y = point
        bl_x, bl_y = bottom_left
        tr_x, tr_y = top_right
        
        return bl_x <= x <= tr_x and bl_y <= y <= tr_y
    
    @staticmethod
    def calculate_polygon_area(polygon: List[Tuple[float, float]]) -> float:
        """
        计算多边形面积（平方米）
        使用Shoelace公式
        
        Args:
            polygon: 多边形顶点坐标列表 [(经度, 纬度), ...]
            
        Returns:
            float: 多边形面积（平方米）
        """
        if len(polygon) < 3:
            return 0.0
        
        # 使用Shoelace公式计算面积
        n = len(polygon)
        area = 0.0
        
        for i in range(n):
            j = (i + 1) % n
            area += polygon[i][0] * polygon[j][1]
            area -= polygon[j][0] * polygon[i][1]
        
        area = abs(area) / 2.0
        
        # 将经纬度面积转换为平方米
        # 这里使用简化的转换，实际应用中可能需要更精确的投影转换
        lat_avg = sum(point[1] for point in polygon) / len(polygon)
        lat_factor = math.cos(math.radians(lat_avg))
        
        # 1度经度约等于111320 * cos(lat) 米
        # 1度纬度约等于110540 米
        area_m2 = area * (111320 * lat_factor) * 110540
        
        return area_m2
    
    @staticmethod
    def calculate_bearing(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """
        计算从点1到点2的方位角（度）
        
        Args:
            point1: 起始点坐标 (经度, 纬度)
            point2: 目标点坐标 (经度, 纬度)
            
        Returns:
            float: 方位角（0-360度，正北为0度，顺时针）
        """
        lng1, lat1 = point1
        lng2, lat2 = point2
        
        # 转换为弧度
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lng = math.radians(lng2 - lng1)
        
        # 计算方位角
        y = math.sin(delta_lng) * math.cos(lat2_rad)
        x = (math.cos(lat1_rad) * math.sin(lat2_rad) - 
             math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(delta_lng))
        
        bearing = math.atan2(y, x)
        bearing = math.degrees(bearing)
        bearing = (bearing + 360) % 360  # 转换为0-360度
        
        return bearing
    
    @staticmethod
    def calculate_midpoint(point1: Tuple[float, float], point2: Tuple[float, float]) -> Tuple[float, float]:
        """
        计算两点的中点坐标
        
        Args:
            point1: 第一个点坐标 (经度, 纬度)
            point2: 第二个点坐标 (经度, 纬度)
            
        Returns:
            Tuple[float, float]: 中点坐标 (经度, 纬度)
        """
        lng1, lat1 = point1
        lng2, lat2 = point2
        
        mid_lng = (lng1 + lng2) / 2.0
        mid_lat = (lat1 + lat2) / 2.0
        
        return (mid_lng, mid_lat)
    
    @staticmethod
    def parse_coord_string(coord_str: str) -> Optional[Tuple[float, float]]:
        """
        解析坐标字符串，支持多种格式
        
        Args:
            coord_str: 坐标字符串，格式如 "lng,lat" 或 "lng lat"
            
        Returns:
            Optional[Tuple[float, float]]: 解析后的坐标 (经度, 纬度)，解析失败返回None
        """
        if not coord_str or not coord_str.strip():
            return None
        
        try:
            # 尝试逗号分隔
            if ',' in coord_str:
                parts = coord_str.split(',')
                if len(parts) == 2:
                    lng = float(parts[0].strip())
                    lat = float(parts[1].strip())
                    return (lng, lat)
            
            # 尝试空格分隔
            parts = coord_str.split()
            if len(parts) == 2:
                lng = float(parts[0].strip())
                lat = float(parts[1].strip())
                return (lng, lat)
            
        except (ValueError, IndexError):
            pass
        
        return None
    
    @staticmethod
    def format_coord_string(coord: Tuple[float, float], precision: int = 6) -> str:
        """
        格式化坐标为字符串
        
        Args:
            coord: 坐标 (经度, 纬度)
            precision: 小数位数
            
        Returns:
            str: 格式化后的坐标字符串 "lng,lat"
        """
        lng, lat = coord
        return f"{lng:.{precision}f},{lat:.{precision}f}"
    
    @staticmethod
    def validate_coord_range(coord: Tuple[float, float]) -> bool:
        """
        验证坐标范围是否有效
        
        Args:
            coord: 坐标 (经度, 纬度)
            
        Returns:
            bool: True表示坐标有效，False表示无效
        """
        lng, lat = coord
        
        # 经度范围：-180 到 180
        if not (-180 <= lng <= 180):
            return False
        
        # 纬度范围：-90 到 90
        if not (-90 <= lat <= 90):
            return False
        
        return True
    
    @staticmethod
    def parse_coords_string(coords_str: str, separator: str = ';') -> List[Tuple[float, float]]:
        """
        解析坐标字符串，转换为经纬度坐标数组
        
        Args:
            coords_str: 坐标字符串，格式如 "lng1,lat1;lng2,lat2;lng3,lat3"
            separator: 坐标点之间的分隔符，默认为分号 ';'
            
        Returns:
            List[Tuple[float, float]]: 坐标点列表 [(经度, 纬度), ...]
            
        Example:
            >>> coords_str = "121.1,31.4;121.2,31.5;121.3,31.6"
            >>> coords = GeoCalculator.parse_coords_string(coords_str)
            >>> print(coords)
            [(121.1, 31.4), (121.2, 31.5), (121.3, 31.6)]
        """
        if not coords_str or not coords_str.strip():
            return []
        
        try:
            # 按分隔符分割坐标点
            points_str = coords_str.split(separator)
            coords = []
            
            for point_str in points_str:
                point_str = point_str.strip()
                if not point_str:
                    continue
                    
                # 按逗号分割经度和纬度
                if ',' in point_str:
                    parts = point_str.split(',')
                    if len(parts) >= 2:
                        lng = float(parts[0].strip())
                        lat = float(parts[1].strip())
                        coords.append((lng, lat))
                else:
                    # 尝试空格分隔
                    parts = point_str.split()
                    if len(parts) >= 2:
                        lng = float(parts[0].strip())
                        lat = float(parts[1].strip())
                        coords.append((lng, lat))
            
            return coords
            
        except (ValueError, IndexError) as e:
            print(f"解析坐标字符串失败：{e}")
            return []
    
    @staticmethod
    def format_coords_string(coords: List[Tuple[float, float]], 
                           separator: str = ';', 
                           precision: int = 6) -> str:
        """
        将坐标数组格式化为坐标字符串
        
        Args:
            coords: 坐标点列表 [(经度, 纬度), ...]
            separator: 坐标点之间的分隔符，默认为分号 ';'
            precision: 小数位数，默认为6位
            
        Returns:
            str: 格式化后的坐标字符串
            
        Example:
            >>> coords = [(121.1, 31.4), (121.2, 31.5), (121.3, 31.6)]
            >>> coords_str = GeoCalculator.format_coords_string(coords)
            >>> print(coords_str)
            "121.100000,31.400000;121.200000,31.500000;121.300000,31.600000"
        """
        if not coords:
            return ""
        
        formatted_points = []
        for lng, lat in coords:
            formatted_points.append(f"{lng:.{precision}f},{lat:.{precision}f}")
        
        return separator.join(formatted_points)


class CoordConverter:
    """
    坐标系转换工具类
    支持多种坐标系之间的转换：
    - GCJ-02：高德地图、腾讯地图使用（火星坐标系）
    - WGS84：国际标准坐标系，GPS使用
    - BD-09：百度地图使用
    
    说明：
    - 高德地图和腾讯地图都使用 GCJ-02 坐标系
    - 本类提供精确的 GCJ-02 ↔ WGS84 转换算法
    """
    
    # 腾讯坐标系简易转换参数（仅用于快速近似转换，不推荐）
    CONVERSION_PARAMS = {
        'tencent_to_wgs84': {
            'x_offset': 0.0065,
            'y_offset': 0.0060
        },
        'wgs84_to_tencent': {
            'x_offset': -0.0065,
            'y_offset': -0.0060
        }
    }
    
    @staticmethod
    def tencent_to_wgs84(coord: Tuple[float, float]) -> Tuple[float, float]:
        """
        腾讯坐标系转WGS84坐标系
        
        Args:
            coord: 腾讯坐标系坐标 (经度, 纬度)
            
        Returns:
            Tuple[float, float]: WGS84坐标系坐标 (经度, 纬度)
        """
        lng, lat = coord
        params = CoordConverter.CONVERSION_PARAMS['tencent_to_wgs84']
        
        wgs84_lng = lng - params['x_offset']
        wgs84_lat = lat - params['y_offset']
        
        return (wgs84_lng, wgs84_lat)
    
    @staticmethod
    def wgs84_to_tencent(coord: Tuple[float, float]) -> Tuple[float, float]:
        """
        WGS84坐标系转腾讯坐标系
        
        Args:
            coord: WGS84坐标系坐标 (经度, 纬度)
            
        Returns:
            Tuple[float, float]: 腾讯坐标系坐标 (经度, 纬度)
        """
        lng, lat = coord
        params = CoordConverter.CONVERSION_PARAMS['wgs84_to_tencent']
        
        tencent_lng = lng - params['x_offset']
        tencent_lat = lat - params['y_offset']
        
        return (tencent_lng, tencent_lat)
    
    #新增高德转84坐标系
    @staticmethod
    def _is_out_of_china(lon: float, lat: float) -> bool:
        """
        判断坐标是否在中国境外
        
        Args:
            lon: 经度
            lat: 纬度
            
        Returns:
            bool: True表示在中国境外，False表示在中国境内
        """
        # 中国大陆及周边范围
        if lon < 72.004 or lon > 137.8347:
            return True
        if lat < 0.8293 or lat > 55.8271:
            return True
        return False
    
    @staticmethod
    def _transform_lat(x: float, y: float) -> float:
        """
        纬度转换辅助方法（GCJ-02 加密算法的一部分）
        
        Args:
            x: 经度偏移
            y: 纬度偏移
            
        Returns:
            float: 转换后的纬度值
        """
        ret = -100.0 + 2.0 * x + 3.0 * y + 0.2 * y * y + 0.1 * x * y + 0.2 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(y * math.pi) + 40.0 * math.sin(y / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (160.0 * math.sin(y / 12.0 * math.pi) + 320 * math.sin(y * math.pi / 30.0)) * 2.0 / 3.0
        return ret
    
    @staticmethod
    def _transform_lon(x: float, y: float) -> float:
        """
        经度转换辅助方法（GCJ-02 加密算法的一部分）
        
        Args:
            x: 经度偏移
            y: 纬度偏移
            
        Returns:
            float: 转换后的经度值
        """
        ret = 300.0 + x + 2.0 * y + 0.1 * x * x + 0.1 * x * y + 0.1 * math.sqrt(abs(x))
        ret += (20.0 * math.sin(6.0 * x * math.pi) + 20.0 * math.sin(2.0 * x * math.pi)) * 2.0 / 3.0
        ret += (20.0 * math.sin(x * math.pi) + 40.0 * math.sin(x / 3.0 * math.pi)) * 2.0 / 3.0
        ret += (150.0 * math.sin(x / 12.0 * math.pi) + 300.0 * math.sin(x / 30.0 * math.pi)) * 2.0 / 3.0
        return ret
    
    @staticmethod
    def _delta(lat: float, lon: float) -> Tuple[float, float]:
        """
        计算坐标偏移量（GCJ-02 加密算法的核心）
        
        Args:
            lat: 纬度
            lon: 经度
            
        Returns:
            Tuple[float, float]: 纬度偏移量和经度偏移量 (dLat, dLon)
        """
        a = 6378245.0  # 长半轴
        ee = 0.00669342162296594323  # 偏心率平方
        
        d_lat = CoordConverter._transform_lat(lon - 105.0, lat - 35.0)
        d_lon = CoordConverter._transform_lon(lon - 105.0, lat - 35.0)
        
        rad_lat = (lat / 180.0) * math.pi
        magic = math.sin(rad_lat)
        magic = 1 - ee * magic * magic
        sqrt_magic = math.sqrt(magic)
        
        d_lat = (d_lat * 180.0) / ((a * (1 - ee)) / (magic * sqrt_magic) * math.pi)
        d_lon = (d_lon * 180.0) / (a / sqrt_magic * math.cos(rad_lat) * math.pi)
        
        return (d_lat, d_lon)
    
    @staticmethod
    def gcj02_to_wgs84(coord: Tuple[float, float]) -> Tuple[float, float]:
        """
        GCJ-02（高德/国测局坐标）转 WGS84 坐标
        使用迭代法进行精确转换
        
        Args:
            coord: GCJ-02坐标 (经度, 纬度)
            
        Returns:
            Tuple[float, float]: WGS84坐标 (经度, 纬度)
        """
        gcj_lon, gcj_lat = coord
        
        # 判断是否在中国境外，如果在境外则不进行转换
        if CoordConverter._is_out_of_china(gcj_lon, gcj_lat):
            return (gcj_lon, gcj_lat)
        
        # 使用迭代法进行精确转换
        wgs_lon = gcj_lon
        wgs_lat = gcj_lat
        
        for i in range(10):
            temp_gcj_lon, temp_gcj_lat = CoordConverter.wgs84_to_gcj02((wgs_lon, wgs_lat))
            d_lon = temp_gcj_lon - gcj_lon
            d_lat = temp_gcj_lat - gcj_lat
            
            wgs_lon -= d_lon
            wgs_lat -= d_lat
            
            # 精度足够则提前退出
            if abs(d_lon) < 1e-9 and abs(d_lat) < 1e-9:
                break
        
        return (wgs_lon, wgs_lat)
    
    @staticmethod
    def wgs84_to_gcj02(coord: Tuple[float, float]) -> Tuple[float, float]:
        """
        WGS84 坐标转 GCJ-02（高德/国测局坐标）
        
        Args:
            coord: WGS84坐标 (经度, 纬度)
            
        Returns:
            Tuple[float, float]: GCJ-02坐标 (经度, 纬度)
        """
        wgs_lon, wgs_lat = coord
        
        # 判断是否在中国境外，如果在境外则不进行转换
        if CoordConverter._is_out_of_china(wgs_lon, wgs_lat):
            return (wgs_lon, wgs_lat)
        
        d_lat, d_lon = CoordConverter._delta(wgs_lat, wgs_lon)
        return (wgs_lon + d_lon, wgs_lat + d_lat)
    
    # ========== 简洁的别名方法（与腾讯坐标转换风格一致） ==========
    


class GridCalculator:
    """
    网格计算工具类
    专门用于太仓线网项目的网格相关计算
    """
    
    @staticmethod
    def calculate_grid_center(bottom_left: Tuple[float, float], 
                            top_right: Tuple[float, float]) -> Tuple[float, float]:
        """
        计算网格中心点坐标
        
        Args:
            bottom_left: 网格左下角坐标 (经度, 纬度)
            top_right: 网格右上角坐标 (经度, 纬度)
            
        Returns:
            Tuple[float, float]: 网格中心点坐标 (经度, 纬度)
        """
        return GeoCalculator.calculate_midpoint(bottom_left, top_right)
    
    @staticmethod
    def calculate_grid_area(bottom_left: Tuple[float, float], 
                          top_right: Tuple[float, float]) -> float:
        """
        计算网格面积（平方米）
        
        Args:
            bottom_left: 网格左下角坐标 (经度, 纬度)
            top_right: 网格右上角坐标 (经度, 纬度)
            
        Returns:
            float: 网格面积（平方米）
        """
        # 构建矩形多边形
        polygon = [
            bottom_left,
            (top_right[0], bottom_left[1]),  # 右下角
            top_right,
            (bottom_left[0], top_right[1])   # 左上角
        ]
        
        return GeoCalculator.calculate_polygon_area(polygon)
    
    @staticmethod
    def is_point_in_grid(point: Tuple[float, float], 
                        bottom_left: Tuple[float, float], 
                        top_right: Tuple[float, float]) -> bool:
        """
        判断点是否在网格内
        
        Args:
            point: 要判断的点坐标 (经度, 纬度)
            bottom_left: 网格左下角坐标 (经度, 纬度)
            top_right: 网格右上角坐标 (经度, 纬度)
            
        Returns:
            bool: True表示点在网格内，False表示在外部
        """
        return GeoCalculator.is_point_in_rectangle(point, bottom_left, top_right)
