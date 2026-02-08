'''
Description: 停车场站视图
Version: 1.0
Autor: 王晨
Date: 2025-10-18
LastEditors: 王晨
LastEditTime: 2025-10-18
'''
from rest_framework.decorators import api_view, action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse, DetailResponse
from dvadmin.utils.request_util import get_and_validate_date_param
from .models import ParkModel
from .serializers import (
    ParkModelSerializer,
    ParkModelListSerializer,
    ParkModelSimpleSerializer,
    ParkModelMapSerializer
)
from dvadmin_twodev.utils.geo.geo_utils import GeoCalculator


class ParkModelViewSet(CustomModelViewSet):
    """
    停车场站管理视图集
    提供标准CRUD接口
    """
    queryset = ParkModel.objects.all()
    serializer_class = ParkModelSerializer

    @action(
        methods=["GET"],
        detail=False,
        url_path="get_all",
        permission_classes=[IsAuthenticated],
    )
    def get_all(self, request):
        """
        获取全量数据
        
        功能说明：
        1. 支持通过 fields 参数控制返回的字段类型
        2. 返回全量数据，不分页
        3. 支持地图展示模式（fields=map），返回WGS84坐标数据
        4. 注意：ParkModel 没有 exec_day 和 expiry_day 字段，不支持时间范围过滤
        
        请求参数：
        - fields: 可选，控制返回字段类型
          * simple: 只返回 id、场站编码、场站名称
          * list: 返回列表序列化器的字段（优化后的字段列表）
          * map: 返回地图展示需要的字段（包含WGS84坐标数据）
          * full: 返回全部字段（默认）
        - date: 可选，指定查询日期（格式：YYYY-MM-DD），当前版本暂未使用
        
        请求示例：
        GET /api/ParkModelViewSet/get_all/?fields=simple
        GET /api/ParkModelViewSet/get_all/?fields=list
        GET /api/ParkModelViewSet/get_all/?fields=map
        GET /api/ParkModelViewSet/get_all/?fields=full
        
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
                    "park_code": "PARK001",
                    "park_name": "太仓客运站停车场",
                    "company_name": "太仓公交公司",
                    "park_address": "江苏省苏州市太仓市...",
                    "station_type": 0,
                    "park_status": 2,
                    "lon84": 121.123456,
                    "lat84": 31.456789
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
                serializer_class = ParkModelSimpleSerializer
            elif fields_type == 'list':
                serializer_class = ParkModelListSerializer
            elif fields_type == 'map':
                serializer_class = ParkModelMapSerializer
            else:  # full 或其他
                serializer_class = ParkModelSerializer

            # 获取基础查询集（应用过滤条件）
            queryset = self.filter_queryset(self.get_queryset())

            # 注意：ParkModel 没有 exec_day 和 expiry_day 字段，不支持 valid_period 方法
            # 如果需要时间过滤，可以基于 create_datetime 或其他字段进行过滤

            # 序列化数据
            serializer = serializer_class(queryset, many=True, request=request)

            return DetailResponse(
                data=serializer.data,
                msg=f"获取成功，共 {len(serializer.data)} 条数据"
            )

        except Exception as e:
            return ErrorResponse(msg=f"获取数据失败: {str(e)}")
