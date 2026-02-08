'''
Description: 车位广告视图
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from dvadmin.utils.viewset import CustomModelViewSet

from .models import VehicleAdPositionModel
from .serializers import (
    VehicleAdPositionModelSerializer,
    VehicleAdPositionModelCreateSerializer,
    VehicleAdPositionModelUpdateSerializer,
    VehicleAdPositionModelListSerializer,
)


class VehicleAdPositionModelViewSet(CustomModelViewSet):
    """
    车位广告管理视图集

    功能说明:
    - 提供车位广告的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作

    标准DRF接口:
    - GET /api/VehicleAdPositionModelViewSet/ - 获取车位广告列表
    - POST /api/VehicleAdPositionModelViewSet/ - 创建车位广告
    - PUT /api/VehicleAdPositionModelViewSet/{id}/ - 更新车位广告
    - PATCH /api/VehicleAdPositionModelViewSet/{id}/ - 部分更新车位广告
    - DELETE /api/VehicleAdPositionModelViewSet/{id}/ - 删除车位广告
    """
    
    # 允许的 HTTP 方法（包含 PATCH）
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']

    # 查询集
    queryset = VehicleAdPositionModel.objects.all()

    # 默认序列化器(用于查询详情)
    serializer_class = VehicleAdPositionModelSerializer

    # 列表序列化器(用于列表展示)
    list_serializer_class = VehicleAdPositionModelListSerializer

    # 创建序列化器
    create_serializer_class = VehicleAdPositionModelCreateSerializer

    # 更新序列化器
    update_serializer_class = VehicleAdPositionModelUpdateSerializer

    # 过滤字段(支持精确查询)
    filter_fields = [
        "id",
        "booking_detail_id",
        "roadline_id",
        "roadline_company_id",
        "resource_id",
        "vehicle_id",
        "allocation_status",
        "enabled_mark",
        "delete_mark",
    ]

    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        "id",
        "booking_detail_id",
        "roadline_id",
        "roadline_company_id",
        "resource_id",
        "vehicle_id",
        "allocation_status",
        "enabled_mark",
        "delete_mark",
    ]

    # 搜索字段(支持模糊查询)
    search_fields = ["roadline_name", "roadline_company_name", "vehicle_no"]

    # 排序字段
    ordering_fields = [
        "create_datetime",
        "update_datetime",
        "reserved_start_date",
        "reserved_end_date",
    ]

    # 默认排序
    ordering = ["booking_detail_id", "roadline_id", "vehicle_id"]

