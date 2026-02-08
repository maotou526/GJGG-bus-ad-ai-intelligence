'''
Description: 地图查询管理视图
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.db import transaction
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from dvadmin_twodev.basedata.roadline.models import RoadlineModel
from dvadmin_twodev.basedata.roadline_detail.models import RoadlineDetailModel
from dvadmin_twodev.basedata.roadline_stop_rel.models import RoadlineStopRelModel
from conf.env import AMAP_API_KEY


class MapManageModelViewSet(CustomModelViewSet):
    """
    地图查询管理视图集
    
    功能说明：
    - 提供地图查询相关接口
    - 获取高德地图API Key
    - 地图查询线路列表（包含轨迹和站点信息）
    
    自定义接口：
    - GET /api/MapManageModelViewSet/get_amap_api_key/ - 获取高德地图API Key
    - GET /api/MapManageModelViewSet/get_manage_list/ - 地图查询线路列表
    """
    
    # 由于这是查询视图，不需要模型和序列化器
    queryset = RoadlineModel.objects.none()
    serializer_class = None
    
    @action(
        methods=["GET"],
        detail=False,
        url_path="get_amap_api_key",
        permission_classes=[IsAuthenticated],
    )
    def get_amap_api_key(self, request):
        """
        获取高德地图API Key
        
        功能说明：
        - 从后端配置文件中读取AMAP_API_KEY
        - 返回给前端用于加载高德地图API
        
        请求方式：GET /api/MapManageModelViewSet/get_amap_api_key/
        
        返回结果：
        {
            "code": 2000,
            "msg": "获取成功",
            "data": "40d167564ff31e9c1a7ead7d30e407be"
        }
        """
        try:
            api_key = AMAP_API_KEY
            if not api_key:
                return ErrorResponse(msg="高德地图API Key未配置")
            
            return DetailResponse(
                data=api_key,
                msg="获取成功"
            )
        except Exception as e:
            return ErrorResponse(msg=f"获取高德地图API Key失败: {str(e)}")
    
    @action(
        methods=["GET"],
        detail=False,
        url_path="get_manage_list",
        permission_classes=[IsAuthenticated],
    )
    def get_manage_list(self, request):
        """
        地图查询 - 获取线路列表（用于地图展示）
        
        功能说明：
        1. 支持按线路名称（wd）模糊搜索
        2. 支持按线路名称（lineName）精确查询
        3. 支持按营运公司（company）过滤
        4. 返回线路详情（上下行）、轨迹坐标、站点列表等信息
        5. 坐标系统使用GCJ02（高德坐标系）
        
        请求参数：
        - wd: 可选，关键词搜索（线路名称）
        - lineName: 可选，线路名称（精确匹配）
        - company: 可选，营运公司名称
        - limit: 可选，返回数量限制，默认100
        
        请求示例：
        GET /api/MapManageModelViewSet/get_manage_list/?wd=1路
        GET /api/MapManageModelViewSet/get_manage_list/?lineName=101路&company=太仓公交公司
        
        返回结果：
        {
            "code": 2000,
            "msg": "查询成功，共找到 2 条线路",
            "data": {
                "RoadLineList": [
                    {
                        "TblRcdId": 1,  // 线路详情ID
                        "Updown": 0,   // 0-上行，1-下行
                        "Info": {
                            "RoadLine": "1路",  // 线路名称
                            "LineLonLat02": "120.123,31.456;120.124,31.457;..."  // GCJ02轨迹坐标
                        },
                        "StartStation": "起点站",  // 起点名称
                        "EndStation": "终点站",    // 终点名称
                        "RunCompany": "太仓公交公司",  // 营运公司
                        "RunHours": "05:30-22:00",    // 首末班时间
                        "TicketStyle": "2元",          // 票价
                        "StopList": [
                            {
                                "StopId": 1,           // 站点ID
                                "LevelId": 1,          // 站序
                                "LevelName": "站点名称", // 站点名称
                                "StrLon": 120.123,     // GCJ02经度
                                "StrLat": 31.456,      // GCJ02纬度
                                "PathDirection": "上行", // 路径方向
                                "SETime": "05:30"      // 首末班时间（可选）
                            }
                        ]
                    }
                ]
            }
        }
        """
        try:
            # 获取查询参数
            wd = request.query_params.get('wd', '').strip()
            line_name = request.query_params.get('lineName', '').strip()
            company_name = request.query_params.get('company', '').strip()
            limit = int(request.query_params.get('limit', 100))
            
            # 构建查询条件
            roadline_query = RoadlineModel.objects.filter(
                Q(delete_mark=0) | Q(delete_mark__isnull=True)
            ).exclude(enabled_mark=0)
            
            # 关键词搜索（线路名称）
            if wd:
                roadline_query = roadline_query.filter(line_name__icontains=wd)
            
            # 线路名称精确匹配
            if line_name:
                roadline_query = roadline_query.filter(line_name=line_name)
            
            # 营运公司过滤
            if company_name:
                roadline_query = roadline_query.filter(company_name=company_name)
            
            # 限制数量
            roadlines = roadline_query[:limit]
            
            # 构建返回数据
            roadline_list = []
            
            for roadline in roadlines:
                # 获取该线路的所有详情（上行、下行）
                details = RoadlineDetailModel.objects.filter(
                    Q(delete_mark=0) | Q(delete_mark__isnull=True),
                    roadline=roadline
                ).exclude(enabled_mark=0).order_by('up_down')
                
                for detail in details:
                    # 获取站点列表
                    stop_rels = RoadlineStopRelModel.objects.filter(
                        Q(delete_mark=0) | Q(delete_mark__isnull=True),
                        line_dtl_id=detail.id
                    ).exclude(enabled_mark=0).order_by('level_id')
                    
                    # 构建站点列表
                    stop_list = []
                    for stop_rel in stop_rels:
                        # 优先使用关联表中的坐标，如果没有则从站点表获取
                        lon02 = stop_rel.lon02
                        lat02 = stop_rel.lat02
                        stop_code = stop_rel.stop_code  # 优先使用关联表中的站点编号
                        
                        # 通过 stop_code 关联站点表获取详细信息
                        district = None  # 区属
                        roadline_name = None  # 路名
                        stop_address = None  # 站址
                        road_line_list = None  # 停靠线路
                        
                        try:
                            from dvadmin_twodev.basedata.roadline_stop.models import RoadlineStopModel
                            
                            # 优先通过 stop_code 查询站点表
                            stop = None
                            if stop_code:
                                stop = RoadlineStopModel.objects.filter(
                                    Q(delete_mark=0) | Q(delete_mark__isnull=True),
                                    stop_code=stop_code
                                ).first()
                            
                            # 如果通过 stop_code 没找到，尝试通过 stop_id 查询
                            if not stop and stop_rel.stop_id:
                                stop = RoadlineStopModel.objects.filter(
                                    Q(delete_mark=0) | Q(delete_mark__isnull=True),
                                    id=stop_rel.stop_id
                                ).first()
                            
                            if stop:
                                # 获取坐标（如果关联表中没有）
                                if not lon02:
                                    lon02 = stop.lon02
                                if not lat02:
                                    lat02 = stop.lat02
                                # 获取站点编号（如果关联表中没有）
                                if not stop_code:
                                    stop_code = stop.stop_code
                                
                                # 获取站点详细信息
                                district = stop.district
                                roadline_name = stop.roadline_name
                                stop_address = stop.stop_address
                                road_line_list = stop.road_line_list
                        except Exception:
                            pass
                        
                        stop_item = {
                            "StopId": stop_rel.id,
                            "stop_code": stop_code or "",  # 站点编号
                            "LevelId": stop_rel.level_id or 0,
                            "LevelName": stop_rel.level_name or "",
                            "StrLon": float(lon02) if lon02 else None,
                            "StrLat": float(lat02) if lat02 else None,
                            "PathDirection": "上行" if detail.up_down == 0 else "下行",
                            "district": district or "",  # 区属
                            "roadline_name": roadline_name or "",  # 路名
                            "stop_address": stop_address or "",  # 站址
                            "road_line_list": road_line_list or "",  # 停靠线路
                        }
                        
                        # 添加首末班时间（如果有）
                        if detail.start_end_time:
                            stop_item["SETime"] = detail.start_end_time
                        
                        stop_list.append(stop_item)
                    
                    # 解析轨迹坐标
                    line_points = []
                    if detail.lon_lat02:
                        try:
                            # 解析GCJ02坐标字符串 "120.123,31.456;120.124,31.457;..."
                            points_str = detail.lon_lat02.split(';')
                            for point_str in points_str:
                                if ',' in point_str:
                                    lon, lat = point_str.split(',')
                                    try:
                                        line_points.append([float(lon.strip()), float(lat.strip())])
                                    except (ValueError, TypeError):
                                        continue
                        except Exception:
                            pass
                    
                    # 构建线路信息
                    roadline_item = {
                        "TblRcdId": detail.id,  # 使用详情ID作为唯一标识
                        "Updown": detail.up_down or 0,
                        "Info": {
                            "RoadLine": roadline.line_name or "",
                            "LineLonLat02": detail.lon_lat02 or "",
                        },
                        "StartStation": detail.start_name or "",
                        "EndStation": "",  # 终点名称需要从站点列表获取最后一个站点
                        "RunCompany": roadline.company_name or "",
                        "RunHours": detail.start_end_time or "",
                        "TicketStyle": roadline.ticket_price or "",
                        "StopList": stop_list,
                    }
                    
                    # 设置终点站名称（从站点列表获取）
                    if stop_list:
                        last_stop = stop_list[-1]
                        roadline_item["EndStation"] = last_stop.get("LevelName", "")
                    
                    roadline_list.append(roadline_item)
            
            return DetailResponse(
                data={"RoadLineList": roadline_list},
                msg=f"查询成功，共找到 {len(roadline_list)} 条线路"
            )
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return ErrorResponse(msg=f"查询失败: {str(e)}")
    
    @action(
        methods=["GET"],
        detail=True,
        url_path="get_roadline_detail",
        permission_classes=[IsAuthenticated],
    )
    def get_roadline_detail(self, request, pk=None):
        """
        获取线路详情（包含轨迹点数据）
        
        功能说明：
        - 根据线路详情ID获取完整的线路信息
        - 包含轨迹坐标和站点列表
        
        请求方式：GET /api/MapManageModelViewSet/{id}/get_roadline_detail/
        
        返回结果：
        {
            "code": 2000,
            "msg": "获取成功",
            "data": {
                "id": 1,
                "roadline_name": "1路",
                "up_down": 0,
                "start_name": "起点站",
                "start_end_time": "05:30-22:00",
                "lon_lat02": "120.123,31.456;120.124,31.457;...",
                "line_points": [[120.123, 31.456], [120.124, 31.457], ...],
                "stops": [...]
            }
        }
        """
        try:
            detail = RoadlineDetailModel.objects.filter(
                Q(delete_mark=0) | Q(delete_mark__isnull=True),
                id=pk
            ).exclude(enabled_mark=0).select_related('roadline').first()
            
            if not detail:
                return ErrorResponse(msg="线路详情不存在")
            
            # 解析轨迹坐标
            line_points = []
            if detail.lon_lat02:
                try:
                    points_str = detail.lon_lat02.split(';')
                    for point_str in points_str:
                        if ',' in point_str:
                            lon, lat = point_str.split(',')
                            try:
                                line_points.append([float(lon.strip()), float(lat.strip())])
                            except (ValueError, TypeError):
                                continue
                except Exception:
                    pass
            
            # 获取站点列表
            stop_rels = RoadlineStopRelModel.objects.filter(
                Q(delete_mark=0) | Q(delete_mark__isnull=True),
                line_dtl_id=detail.id
            ).exclude(enabled_mark=0).order_by('level_id')
            
            stops = []
            for stop_rel in stop_rels:
                lon02 = stop_rel.lon02
                lat02 = stop_rel.lat02
                
                # 如果关联表中没有坐标，尝试从站点表获取
                if not lon02 or not lat02:
                    try:
                        from dvadmin_twodev.basedata.roadline_stop.models import RoadlineStopModel
                        if stop_rel.stop_id:
                            stop = RoadlineStopModel.objects.filter(
                                Q(delete_mark=0) | Q(delete_mark__isnull=True),
                                id=stop_rel.stop_id
                            ).first()
                            if stop:
                                lon02 = stop.lon02
                                lat02 = stop.lat02
                    except Exception:
                        pass
                
                stops.append({
                    "id": stop_rel.id,
                    "level_id": stop_rel.level_id or 0,
                    "level_name": stop_rel.level_name or "",
                    "lon02": float(lon02) if lon02 else None,
                    "lat02": float(lat02) if lat02 else None,
                })
            
            data = {
                "id": detail.id,
                "roadline_name": detail.roadline.line_name if detail.roadline else "",
                "up_down": detail.up_down or 0,
                "start_name": detail.start_name or "",
                "start_end_time": detail.start_end_time or "",
                "lon_lat02": detail.lon_lat02 or "",
                "line_points": line_points,
                "stops": stops,
            }
            
            return DetailResponse(data=data, msg="获取成功")
            
        except Exception as e:
            return ErrorResponse(msg=f"获取线路详情失败: {str(e)}")
    
    @action(
        methods=["GET"],
        detail=False,
        url_path="get_roadline_stops",
        permission_classes=[IsAuthenticated],
    )
    def get_roadline_stops(self, request):
        """
        获取线路站点列表
        
        功能说明：
        - 根据线路ID和上下行获取站点列表
        - 返回站点坐标和基本信息
        
        请求参数：
        - roadline_id: 可选，线路ID（主表ID）
        - updown: 可选，上下行（0-上行，1-下行）
        
        请求示例：
        GET /api/MapManageModelViewSet/get_roadline_stops/?roadline_id=1&updown=0
        
        返回结果：
        {
            "code": 2000,
            "msg": "获取成功",
            "data": [
                {
                    "id": 1,
                    "level_id": 1,
                    "level_name": "站点名称",
                    "lon02": 120.123,
                    "lat02": 31.456
                }
            ]
        }
        """
        try:
            roadline_id = request.query_params.get('roadline_id')
            updown = request.query_params.get('updown')
            
            # 构建查询条件
            stop_rel_query = RoadlineStopRelModel.objects.filter(
                Q(delete_mark=0) | Q(delete_mark__isnull=True)
            ).exclude(enabled_mark=0)
            
            # 如果提供了线路ID，先找到对应的详情ID
            if roadline_id:
                detail_ids = RoadlineDetailModel.objects.filter(
                    Q(delete_mark=0) | Q(delete_mark__isnull=True),
                    roadline_id=roadline_id
                ).exclude(enabled_mark=0)
                
                if updown is not None:
                    try:
                        updown_int = int(updown)
                        detail_ids = detail_ids.filter(up_down=updown_int)
                    except (ValueError, TypeError):
                        pass
                
                detail_id_list = list(detail_ids.values_list('id', flat=True))
                if detail_id_list:
                    stop_rel_query = stop_rel_query.filter(line_dtl_id__in=detail_id_list)
                else:
                    return DetailResponse(data=[], msg="未找到对应的线路详情")
            
            # 查询站点关联数据
            stop_rels = stop_rel_query.order_by('level_id')
            
            # 构建返回数据
            stops = []
            for stop_rel in stop_rels:
                lon02 = stop_rel.lon02
                lat02 = stop_rel.lat02
                
                # 如果关联表中没有坐标，尝试从站点表获取
                if not lon02 or not lat02:
                    try:
                        from dvadmin_twodev.basedata.roadline_stop.models import RoadlineStopModel
                        if stop_rel.stop_id:
                            stop = RoadlineStopModel.objects.filter(
                                Q(delete_mark=0) | Q(delete_mark__isnull=True),
                                id=stop_rel.stop_id
                            ).first()
                            if stop:
                                lon02 = stop.lon02
                                lat02 = stop.lat02
                    except Exception:
                        pass
                
                stops.append({
                    "id": stop_rel.id,
                    "level_id": stop_rel.level_id or 0,
                    "level_name": stop_rel.level_name or "",
                    "lon02": float(lon02) if lon02 else None,
                    "lat02": float(lat02) if lat02 else None,
                })
            
            return DetailResponse(
                data=stops,
                msg=f"获取成功，共 {len(stops)} 个站点"
            )
            
        except Exception as e:
            return ErrorResponse(msg=f"获取站点列表失败: {str(e)}")
