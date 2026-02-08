"""
Description: 线路走向详情视图
Version: 1.0
Autor: 王晨
Date: 2025-10-14
LastEditors: 王晨
LastEditTime: 2025-10-27
"""
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import SuccessResponse, DetailResponse, ErrorResponse
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .models import RoadlineDetailModel
from dvadmin_twodev.basedata.roadline.models import RoadlineModel
from dvadmin_twodev.utils.geo import CoordConverter
from django.db.models import Q, Avg, Sum, Count
from django.db import transaction
import logging
from django.utils import timezone
from .serializers import (
    RoadlineDetailModelSerializer,
    RoadlineDetailListSerializer,
    RoadlineDetailSimpleSerializer,
    RoadlineDetailImportSerializer,
    RoadlineDetailMapSerializer
)

logger = logging.getLogger(__name__)


def _parse_polyline(polyline_str):
    """
    解析高德 polyline 字符串为坐标列表（GCJ-02 坐标系）
    
    参数：
        polyline_str: 高德 polyline 格式字符串，如 "120.123,30.456;120.124,30.457"
    
    返回：
        list: 坐标列表，如 [{"lng": 120.123, "lat": 30.456}, ...]
    """
    if not polyline_str:
        return []
    
    try:
        coordinates = []
        for point in polyline_str.split(';'):
            if ',' in point:
                lng, lat = point.split(',')
                coordinates.append({
                    'lng': float(lng),
                    'lat': float(lat)
                })
        return coordinates
    except Exception as e:
        logger.warning(f"[Polyline解析] 解析失败: {str(e)}")
        return []


def _convert_polyline_to_wgs84(polyline_str):
    """
    将高德 polyline 字符串（GCJ-02 坐标系）转换为 WGS84 坐标系
    
    参数：
        polyline_str: 高德 polyline 格式字符串（GCJ-02 坐标系）
    
    返回：
        str: 转换后的 polyline 字符串（WGS84 坐标系），格式同输入
    """
    if not polyline_str:
        return ""
    
    try:
        converted_points = []
        for point in polyline_str.split(';'):
            if ',' in point:
                lng, lat = point.split(',')
                gcj02_coord = (float(lng), float(lat))
                # 使用 CoordConverter 进行 GCJ-02 到 WGS84 的转换
                wgs84_coord = CoordConverter.gcj02_to_wgs84(gcj02_coord)
                converted_points.append(f"{wgs84_coord[0]},{wgs84_coord[1]}")
        
        return ';'.join(converted_points)
    except Exception as e:
        logger.error(f"[坐标转换] GCJ-02 转 WGS84 失败: {str(e)}")
        return polyline_str  # 转换失败时返回原始数据


def _format_polyline_response(buslines):
    """
    格式化高德 API 返回的 polyline 数据
    
    参数：
        buslines: 高德 API 返回的路线列表
    
    返回：
        list: 格式化后的路线列表，包含解析后的坐标
    """
    formatted_lines = []
    
    for line in buslines:
        polyline_str = line.get('polyline', '')
        coordinates = _parse_polyline(polyline_str)
        
        formatted_line = {
            'id': line.get('id'),
            'name': line.get('name'),
            'type': line.get('type'),
            'citycode': line.get('citycode'),
            'start_stop': line.get('start_stop'),
            'end_stop': line.get('end_stop'),
            'polyline': polyline_str,  # 保留原始 polyline 字符串
            'coordinates': coordinates,  # 解析后的坐标列表
            'coordinate_count': len(coordinates)  # 坐标点数
        }
        
        # 如果有详细信息，添加到返回数据
        if 'start_time' in line:
            formatted_line['start_time'] = line.get('start_time')
        if 'end_time' in line:
            formatted_line['end_time'] = line.get('end_time')
        if 'company' in line:
            formatted_line['company'] = line.get('company')
        if 'distance' in line:
            formatted_line['distance'] = line.get('distance')
        
        formatted_lines.append(formatted_line)
    
    return formatted_lines


def _calculate_similarity(str1, str2):
    """
    计算两个字符串的相似度（简单的字符匹配度）
    
    参数：
        str1: 字符串1
        str2: 字符串2
    
    返回：
        float: 相似度，范围 0-1
    """
    if not str1 or not str2:
        return 0.0
    
    str1 = str(str1).strip()
    str2 = str(str2).strip()
    
    # 完全相同
    if str1 == str2:
        return 1.0
    
    # 包含关系
    if str1 in str2 or str2 in str1:
        return 0.8
    
    # 计算字符匹配数
    matches = sum(1 for c in str1 if c in str2)
    similarity = matches / max(len(str1), len(str2))
    
    return similarity


def _find_best_matching_line(line_name, start_name, buslines):
    """
    从高德 API 返回的路线列表中找到最符合的路线
    
    参数：
        line_name: 本地线路名称
        start_name: 本地起点名称
        buslines: 高德 API 返回的路线列表
    
    返回：
        dict: 最符合的路线信息，包含 polyline，如果未找到则返回 None
    """
    if not buslines:
        return None
    
    best_match = None
    best_score = 0
    
    for busline in buslines:
        amap_line_name = busline.get('name', '')
        amap_start_stop = busline.get('start_stop', '')
        
        # 计算线路名称相似度（权重 0.6）
        name_similarity = _calculate_similarity(line_name, amap_line_name)
        
        # 计算起点名称相似度（权重 0.4）
        start_similarity = _calculate_similarity(start_name, amap_start_stop)
        
        # 综合得分
        score = name_similarity * 0.6 + start_similarity * 0.4
        
        logger.debug(
            f"[线路匹配] 本地线路: {line_name}({start_name}) vs "
            f"高德线路: {amap_line_name}({amap_start_stop}), "
            f"名称相似度: {name_similarity:.2f}, 起点相似度: {start_similarity:.2f}, "
            f"综合得分: {score:.2f}"
        )
        
        if score > best_score:
            best_score = score
            best_match = busline
    
    # 只有得分大于 0.5 才认为是有效匹配
    if best_score > 0.5:
        logger.info(
            f"[线路匹配] 找到最佳匹配: 本地线路 {line_name}({start_name}) "
            f"-> 高德线路 {best_match.get('name')}({best_match.get('start_stop')}), "
            f"得分: {best_score:.2f}"
        )
        return best_match
    else:
        logger.warning(
            f"[线路匹配] 未找到满足条件的匹配线路: {line_name}({start_name}), "
            f"最高得分: {best_score:.2f}"
        )
        return None


class RoadlineDetailViewSet(CustomModelViewSet):
    """
    线路走向详情管理视图集
    提供标准CRUD接口和数据导入功能
    """
    queryset = RoadlineDetailModel.objects.all()
    serializer_class = RoadlineDetailModelSerializer
    
    # 导入序列化器
    import_serializer_class = RoadlineDetailImportSerializer
    
    # 导入字段配置
    import_field_dict = {
        'line_name': '线路名称',
        'up_down': {
            'title': '上下行',
            'choices': {
                'data': {
                    '上行': 0,
                    '下行': 1,
                }
            }
        },
        'start_name': '起点名称',
        'start_end_time': '首末班时间',
        'line_length': '线路长度（km）',
    }
    
    @action(methods=['GET'], detail=False, url_path='search_amap_bus_lines', permission_classes=[IsAuthenticated])
    def search_amap_bus_lines(self, request):
        """
        高德公交路线关键字查询（带 polyline 坐标解析和坐标系转换）
        
        功能说明：
        1. 调用高德地图 API 进行公交路线关键字查询
        2. 解析返回的 polyline 坐标数据（GCJ-02 坐标系）
        3. 自动转换为 WGS84 坐标系
        4. 返回两种坐标系的数据供前端使用
        
        请求方式：GET /api/RoadlineDetailViewSet/search_amap_bus_lines/
        
        查询参数：
        - keywords: 必填，查询关键字（如：1路、101路等）
        - city: 必填，城市代码或名称（如：310100 表示杭州，320585 表示太仓）
        - page: 可选，当前页数，默认为 1，最大翻页数 10
        - offset: 可选，每页记录数，默认为 20，最大 100
        - extensions: 可选，返回内容控制，可选值：base（基本信息）、all（基本+详细信息），默认 base
        - convert_coord: 可选，是否转换坐标系，默认 true
        
        返回结果示例：
        {
            "code": 2000,
            "msg": "查询成功，共找到 5 条路线",
            "data": {
                "status": "1",
                "info": "ok",
                "infocode": "10000",
                "count": 5,
                "buslines": [
                    {
                        "id": "1234567",
                        "name": "1路",
                        "type": "普通公交",
                        "citycode": "320585",
                        "start_stop": "火车站",
                        "end_stop": "西湖",
                        "polyline_gcj02": "120.123,30.456;120.124,30.457;...",
                        "polyline_wgs84": "120.120,30.450;120.121,30.451;...",
                        "coordinates_gcj02": [
                            {"lng": 120.123, "lat": 30.456},
                            {"lng": 120.124, "lat": 30.457}
                        ],
                        "coordinates_wgs84": [
                            {"lng": 120.120, "lat": 30.450},
                            {"lng": 120.121, "lat": 30.451}
                        ],
                        "coordinate_count": 100
                    },
                    ...
                ]
            }
        }
        """
        from dvadmin_twodev.utils.gaode import GaodeAPI
        
        try:
            # ============= 1. 获取和验证查询参数 =============
            keywords = request.query_params.get('keywords', '').strip()
            city = request.query_params.get('city', '').strip()
            page = request.query_params.get('page', '1')
            offset = request.query_params.get('offset', '20')
            extensions = request.query_params.get('extensions', 'base')
            convert_coord = request.query_params.get('convert_coord', 'true').lower() == 'true'
            
            # 参数验证
            if not keywords:
                return ErrorResponse(msg="缺少必填参数：keywords（查询关键字）")
            
            if not city:
                return ErrorResponse(msg="缺少必填参数：city（城市代码或名称）")
            
            # 参数范围验证
            try:
                page = int(page)
                if page < 1 or page > 10:
                    page = 1
            except (ValueError, TypeError):
                page = 1
            
            try:
                offset = int(offset)
                if offset < 1 or offset > 100:
                    offset = 20
            except (ValueError, TypeError):
                offset = 20
            
            if extensions not in ['base', 'all']:
                extensions = 'base'
            
            logger.info(
                f"[高德公交路线查询] 开始查询，关键字：{keywords}，城市：{city}，"
                f"页数：{page}，每页：{offset}，详情：{extensions}，坐标转换：{convert_coord}"
            )
            
            # ============= 2. 初始化高德API客户端 =============
            try:
                gaode = GaodeAPI()
            except ValueError as e:
                logger.error(f"[高德公交路线查询] 高德API初始化失败：{str(e)}")
                return ErrorResponse(msg=f"高德API初始化失败：{str(e)}")
            
            # ============= 3. 调用高德API查询公交路线 =============
            try:
                result = gaode._request('/v3/bus/linename', {
                    'keywords': keywords,
                    'city': city,
                    'page': page,
                    'offset': offset,
                    'extensions': extensions
                })
                
                # 处理返回数据
                buslines = result.get('buslines', [])
                
                # ============= 4. 解析和转换 polyline 坐标数据 =============
                formatted_buslines = []
                total_coordinates = 0
                
                for line in buslines:
                    polyline_gcj02 = line.get('polyline', '')
                    coordinates_gcj02 = _parse_polyline(polyline_gcj02)
                    
                    formatted_line = {
                        'id': line.get('id'),
                        'name': line.get('name'),
                        'type': line.get('type'),
                        'citycode': line.get('citycode'),
                        'start_stop': line.get('start_stop'),
                        'end_stop': line.get('end_stop'),
                        'polyline_gcj02': polyline_gcj02,  # GCJ-02 坐标系
                        'coordinates_gcj02': coordinates_gcj02,  # GCJ-02 坐标列表
                        'coordinate_count': len(coordinates_gcj02)
                    }
                    
                    # 如果需要坐标转换，转换为 WGS84
                    if convert_coord and polyline_gcj02:
                        polyline_wgs84 = _convert_polyline_to_wgs84(polyline_gcj02)
                        coordinates_wgs84 = _parse_polyline(polyline_wgs84)
                        formatted_line['polyline_wgs84'] = polyline_wgs84  # WGS84 坐标系
                        formatted_line['coordinates_wgs84'] = coordinates_wgs84  # WGS84 坐标列表
                    
                    # 添加其他可选字段
                    if 'start_time' in line:
                        formatted_line['start_time'] = line.get('start_time')
                    if 'end_time' in line:
                        formatted_line['end_time'] = line.get('end_time')
                    if 'company' in line:
                        formatted_line['company'] = line.get('company')
                    if 'distance' in line:
                        formatted_line['distance'] = line.get('distance')
                    
                    formatted_buslines.append(formatted_line)
                    total_coordinates += len(coordinates_gcj02)
                
                logger.info(
                    f"[高德公交路线查询] 查询成功，关键字：{keywords}，城市：{city}，"
                    f"找到 {len(formatted_buslines)} 条路线，共 {total_coordinates} 个坐标点"
                )
                
                # ============= 5. 返回成功结果 =============
                return SuccessResponse(
                    data={
                        'status': result.get('status'),
                        'info': result.get('info'),
                        'infocode': result.get('infocode'),
                        'count': len(formatted_buslines),
                        'buslines': formatted_buslines,
                        'total_coordinates': total_coordinates,
                        'coordinate_systems': ['gcj02'] + (['wgs84'] if convert_coord else [])
                    },
                    msg=f"查询成功，共找到 {len(formatted_buslines)} 条路线，{total_coordinates} 个坐标点"
                )
            
            except Exception as e:
                error_msg = str(e)
                logger.warning(
                    f"[高德公交路线查询] 查询失败，关键字：{keywords}，城市：{city}，"
                    f"错误：{error_msg}"
                )
                return ErrorResponse(msg=f"高德API查询失败：{error_msg}")
        
        except Exception as e:
            logger.error(f"[高德公交路线查询] 执行失败：{str(e)}", exc_info=True)
            return ErrorResponse(msg=f"查询失败：{str(e)}")
    
    @action(methods=['POST'], detail=False, url_path='batch_fill_poi', permission_classes=[IsAuthenticated])
    def batch_fill_poi(self, request):
        """
        批量填充线路 POI 信息（通过高德 API 查询 polyline）
        
        功能说明：
        1. 遍历所有线路走向数据
        2. 根据线路名称和起点名称调用高德 API 查询公交路线
        3. 从返回结果中找到最符合的路线（基于名称和起点相似度）
        4. 提取 polyline 数据填充到 poi 字段
        5. 支持按城市、线路ID、是否强制更新等条件过滤
        
        请求方式：POST /api/RoadlineDetailViewSet/batch_fill_poi/
        
        请求参数：
        {
            "detail_ids": [1, 2, 3],     // 可选，指定线路走向ID列表，不传则处理全部
            "city": "320585",             // 可选，城市adcode，默认320585（太仓）
            "roadline_ids": [1, 2],       // 可选，指定线路ID列表
            "force_update": false,        // 可选，是否强制更新已有数据，默认false
            "batch_size": 100,            // 可选，进度日志输出间隔，默认100
            "delay": 0.2                  // 可选，每次API调用后的延迟秒数，默认0.2秒
        }
        
        返回结果：
        {
            "code": 2000,
            "data": {
                "total": 100,
                "success": 95,
                "failed": 5,
                "skipped": 10,
                "failed_items": [...],
                "api_call_count": 95,
                "total_coordinates": 12500
            },
            "msg": "批量填充完成！成功 95 条，失败 5 条，跳过 10 条"
        }
        """
        from dvadmin_twodev.utils.gaode import GaodeAPI
        from django.db import transaction
        import time
        
        try:
            # ============= 0. 获取配置参数 =============
            detail_ids = request.data.get('detail_ids', [])
            city = request.data.get('city', '320585')  # 默认太仓
            roadline_ids = request.data.get('roadline_ids', [])
            force_update = request.data.get('force_update', False)
            batch_size = int(request.data.get('batch_size', 100))
            delay = float(request.data.get('delay', 0.2))
            
            # 初始化高德API客户端
            try:
                gaode = GaodeAPI()
                logger.info(f"[批量填充POI] 高德API初始化成功，城市: {city}, 批次大小: {batch_size}, 延迟: {delay}秒")
            except ValueError as e:
                logger.error(f"[批量填充POI] 高德API初始化失败：{str(e)}")
                return ErrorResponse(msg=f"高德API初始化失败：{str(e)}")
            
            with transaction.atomic():
                # ============= 1. 获取待处理的线路走向 =============
                if detail_ids:
                    details_query = self.queryset.filter(id__in=detail_ids)
                else:
                    details_query = self.queryset.filter(
                        Q(delete_mark=0) | Q(delete_mark__isnull=True)
                    ).exclude(enabled_mark=0)
                
                # 按线路ID过滤
                if roadline_ids:
                    details_query = details_query.filter(roadline_id__in=roadline_ids)
                
                # 如果不是强制更新，只处理 poi 为空的记录
                if not force_update:
                    details_query = details_query.filter(
                        Q(poi__isnull=True) | Q(poi='')
                    )
                
                details = list(details_query)
                total_count = len(details)
                
                logger.info(f"[批量填充POI] 共有 {total_count} 条线路走向待处理")
                
                if total_count == 0:
                    return ErrorResponse(msg="没有需要处理的线路走向")
                
                # ============= 2. 遍历线路走向调用高德API =============
                success_count = 0
                failed_count = 0
                skipped_count = 0
                failed_items = []
                api_call_count = 0
                total_coordinates = 0
                
                for idx, detail in enumerate(details):
                    try:
                        # 每批次输出进度日志
                        if idx > 0 and idx % batch_size == 0:
                            logger.info(f"[批量填充POI] 已处理 {idx}/{total_count} 条线路走向...")
                        
                        # 获取线路名称和起点名称
                        line_name = detail.roadline.line_name if detail.roadline else ''
                        start_name = detail.start_name or ''
                        
                        if not line_name:
                            logger.warning(f"[批量填充POI] 线路走向 ID={detail.id} 没有关联线路，跳过")
                            skipped_count += 1
                            continue
                        
                        logger.debug(f"[批量填充POI] 处理线路走向: {line_name}({start_name})")
                        
                        # ============= 3. 调用高德API查询公交路线 =============
                        try:
                            result = gaode._request('/v3/bus/linename', {
                                'keywords': line_name,
                                'city': city,
                                'offset': 20  # 获取前20条结果用于匹配
                            })
                            api_call_count += 1
                            
                            # 添加延迟避免QPS限流
                            time.sleep(delay)
                            
                            buslines = result.get('buslines', [])
                            
                            # ============= 4. 找到最符合的路线 =============
                            best_match = _find_best_matching_line(line_name, start_name, buslines)
                            
                            if best_match:
                                # 获取 polyline（GCJ-02 坐标系）并解析坐标
                                polyline_gcj02 = best_match.get('polyline', '')
                                coordinates_gcj02 = _parse_polyline(polyline_gcj02)
                                
                                if polyline_gcj02:
                                    # ============= 坐标系转换 =============
                                    # 1. 保存原始 GCJ-02 坐标到 lon_lat02 字段
                                    detail.lon_lat02 = polyline_gcj02
                                    
                                    # 2. 转换为 WGS84 坐标系并保存到 lon_lat84 字段
                                    polyline_wgs84 = _convert_polyline_to_wgs84(polyline_gcj02)
                                    detail.lon_lat84 = polyline_wgs84
                                    
                                    # 3. 保存原始 polyline 到 poi 字段（用于兼容）
                                    detail.poi = polyline_gcj02
                                    detail.save()
                                    
                                    success_count += 1
                                    total_coordinates += len(coordinates_gcj02)
                                    
                                    logger.info(
                                        f"[批量填充POI] 成功填充: {line_name}({start_name}) "
                                        f"-> {best_match.get('name')}({best_match.get('start_stop')}), "
                                        f"坐标点数: {len(coordinates_gcj02)}, "
                                        f"已转换为 WGS84 坐标系"
                                    )
                                else:
                                    logger.warning(f"[批量填充POI] 线路 {line_name} 的 polyline 为空")
                                    failed_items.append({
                                        'detail_id': detail.id,
                                        'line_name': line_name,
                                        'start_name': start_name,
                                        'reason': 'polyline 为空'
                                    })
                                    failed_count += 1
                            else:
                                logger.warning(f"[批量填充POI] 未找到匹配的线路: {line_name}({start_name})")
                                failed_items.append({
                                    'detail_id': detail.id,
                                    'line_name': line_name,
                                    'start_name': start_name,
                                    'reason': '未找到匹配的线路'
                                })
                                failed_count += 1
                        
                        except Exception as e:
                            error_msg = str(e)
                            logger.error(
                                f"[批量填充POI] 线路 {line_name} API调用失败: {error_msg}",
                                exc_info=True
                            )
                            failed_items.append({
                                'detail_id': detail.id,
                                'line_name': line_name,
                                'start_name': start_name,
                                'reason': f'API调用失败: {error_msg}'
                            })
                            failed_count += 1
                    
                    except Exception as e:
                        logger.error(
                            f"[批量填充POI] 处理线路走向 ID={detail.id} 失败: {str(e)}",
                            exc_info=True
                        )
                        failed_items.append({
                            'detail_id': detail.id,
                            'line_name': detail.roadline.line_name if detail.roadline else 'N/A',
                            'start_name': detail.start_name or 'N/A',
                            'reason': str(e)
                        })
                        failed_count += 1
                
                # ============= 5. 返回结果 =============
                data = {
                    'total': total_count,
                    'success': success_count,
                    'failed': failed_count,
                    'skipped': skipped_count,
                    'failed_items': failed_items[:50],  # 只返回前50个失败项
                    'api_call_count': api_call_count,
                    'total_coordinates': total_coordinates
                }
                
                logger.info(
                    f"[批量填充POI] 完成！总计 {total_count} 条，"
                    f"成功 {success_count} 条，失败 {failed_count} 条，跳过 {skipped_count} 条，"
                    f"API调用 {api_call_count} 次，总坐标点数 {total_coordinates}"
                )
                
                # 输出失败详情
                if failed_items:
                    logger.warning(f"[批量填充POI] 失败详情（共 {len(failed_items)} 个）：")
                    for item in failed_items[:10]:  # 只输出前10个
                        logger.warning(
                            f"  - 线路 {item['line_name']}({item['start_name']}): {item['reason']}"
                        )
                
                msg = (f"批量填充完成！成功 {success_count} 条，失败 {failed_count} 条，"
                       f"跳过 {skipped_count} 条，共 {total_coordinates} 个坐标点")
                
                return SuccessResponse(data=data, msg=msg)
        
        except Exception as e:
            logger.error(f"[批量填充POI] 执行失败: {str(e)}", exc_info=True)
            return ErrorResponse(msg=f"批量填充失败: {str(e)}")
    
    @action(methods=['GET'], detail=False, url_path='get_all', permission_classes=[IsAuthenticated])
    def get_all(self, request):
        """
        获取全量数据（仅有效时间范围内的数据）
        
        功能说明：
        1. 自动过滤有效时间范围内的数据（exec_day <= 当前日期 <= expiry_day）
        2. 支持通过 fields 参数控制返回的字段类型
        3. 返回全量数据，不分页
        4. 支持地图展示模式（fields=map），返回WGS84坐标数据
        
        请求参数：
        - fields: 可选，控制返回字段类型
          * simple: 只返回 id、线路名称、上下行
          * list: 返回列表序列化器的字段（优化后的字段列表）
          * map: 返回地图展示需要的字段（包含WGS84坐标数据）
          * full: 返回全部字段（默认）
        - date: 可选，指定查询日期（格式：YYYY-MM-DD），默认为当前日期
        
        请求示例：
        GET /api/RoadlineDetailViewSet/get_all/?fields=simple
        GET /api/RoadlineDetailViewSet/get_all/?fields=list
        GET /api/RoadlineDetailViewSet/get_all/?fields=map
        GET /api/RoadlineDetailViewSet/get_all/?fields=full
        GET /api/RoadlineDetailViewSet/get_all/?fields=map&date=2025-01-01
        
        返回结果：
        {
            "code": 2000,
            "msg": "获取成功，共 100 条数据",
            "data": [...]
        }
        
        地图模式（fields=map）返回示例：
        {
            "code": 2000,
            "msg": "获取成功，共 100 条数据",
            "data": [
                {
                    "id": 1,
                    "roadline": 1,
                    "roadline_name": "1路",
                    "up_down": 0,
                    "up_down_display": "上行",
                    "start_name": "火车站",
                    "start_end_time": "05:30-22:00",
                    "coordinates_wgs84": [
                        {"lng": 120.123, "lat": 30.456},
                        {"lng": 120.124, "lat": 30.457}
                    ],
                    "line_length": 12.5
                },
                ...
            ]
        }
        """
    
        try:
            # 获取字段类型参数
            fields_type = request.query_params.get('fields', 'full').lower()
            
            # 根据参数选择序列化器
            if fields_type == 'simple':
                serializer_class = RoadlineDetailSimpleSerializer
            elif fields_type == 'list':
                serializer_class = RoadlineDetailListSerializer
            elif fields_type == 'map':
                serializer_class = RoadlineDetailMapSerializer
            else:  # full 或其他
                serializer_class = RoadlineDetailModelSerializer
            
            # 获取基础查询集并应用所有过滤条件（filter_fields 和 search_fields）
            queryset = self.filter_queryset(super().get_queryset())
            
            # 应用时间范围过滤（传递默认日期为当前日期，保持原有行为）
            queryset, error_response = self._apply_valid_period_filter(
                request, 
                queryset, 
                default_date=timezone.now().date()
            )
            if error_response:
                return error_response
                        
            # 序列化数据
            serializer = serializer_class(queryset, many=True, request=request)
            
            return DetailResponse(
                data=serializer.data,
                msg=f"获取成功，共 {len(serializer.data)} 条数据"
            )
        
        except Exception as e:
            logger.error(f"[获取全量数据] 执行失败: {str(e)}", exc_info=True)
            return ErrorResponse(msg=f"获取数据失败: {str(e)}")
