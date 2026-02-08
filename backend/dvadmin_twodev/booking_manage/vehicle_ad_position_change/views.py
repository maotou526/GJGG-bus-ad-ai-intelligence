'''
Description: 车位广告变更历史视图
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from dvadmin.utils.viewset import CustomModelViewSet

from .models import VehicleAdPositionChangeModel
from .serializers import (
    VehicleAdPositionChangeModelSerializer,
    VehicleAdPositionChangeModelCreateSerializer,
    VehicleAdPositionChangeModelListSerializer,
)


class VehicleAdPositionChangeModelViewSet(CustomModelViewSet):
    """
    车位广告变更历史管理视图集

    功能说明:
    - 提供车位广告变更历史的查询与记录功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能

    标准DRF接口:
    - GET /api/VehicleAdPositionChangeModelViewSet/ - 获取变更历史列表
    - POST /api/VehicleAdPositionChangeModelViewSet/ - 创建变更历史记录
    - GET /api/VehicleAdPositionChangeModelViewSet/{id}/ - 获取变更历史详情
    """

    # 查询集
    queryset = VehicleAdPositionChangeModel.objects.all()

    # 默认序列化器(用于查询详情)
    serializer_class = VehicleAdPositionChangeModelSerializer

    # 列表序列化器(用于列表展示)
    list_serializer_class = VehicleAdPositionChangeModelListSerializer

    # 创建序列化器
    create_serializer_class = VehicleAdPositionChangeModelCreateSerializer

    # 过滤字段(支持精确查询)
    filter_fields = [
        "id",
        "booking_order_id",
        "booking_detail_id",
        "action_type",
        "position_id",
        "roadline_id",
        "roadline_company_id",
        "vehicle_id",
        "resource_id",
        "change_node",
        "operator_id",
        "enabled_mark",
        "delete_mark",
    ]

    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = filter_fields

    # 搜索字段(支持模糊查询)
    search_fields = [
        "roadline_name",
        "roadline_company_name",
        "vehicle_no",
        "change_reason",
    ]

    # 排序字段
    ordering_fields = [
        "operation_time",
        "create_datetime",
        "update_datetime",
        "action_type",
    ]

    # 默认排序
    ordering = ["-operation_time"]
