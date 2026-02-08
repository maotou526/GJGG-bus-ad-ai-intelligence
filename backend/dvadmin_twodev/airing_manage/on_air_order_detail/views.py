'''
Description: 上刊订单明细视图
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from dvadmin.utils.viewset import CustomModelViewSet

from .models import OnAirOrderDetailModel
from .serializers import (
    OnAirOrderDetailModelSerializer,
    OnAirOrderDetailModelCreateSerializer,
    OnAirOrderDetailModelUpdateSerializer,
    OnAirOrderDetailModelListSerializer,
)


class OnAirOrderDetailModelViewSet(CustomModelViewSet):
    """
    上刊订单明细管理视图集

    功能说明:
    - 提供上刊订单明细的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作

    标准DRF接口:
    - GET /api/OnAirOrderDetailModelViewSet/ - 获取上刊订单明细列表
    - POST /api/OnAirOrderDetailModelViewSet/ - 创建上刊订单明细
    - PUT /api/OnAirOrderDetailModelViewSet/{id}/ - 更新上刊订单明细
    - PATCH /api/OnAirOrderDetailModelViewSet/{id}/ - 部分更新上刊订单明细
    - DELETE /api/OnAirOrderDetailModelViewSet/{id}/ - 删除上刊订单明细
    """

    # 查询集
    queryset = OnAirOrderDetailModel.objects.all()

    # 默认序列化器(用于查询详情)
    serializer_class = OnAirOrderDetailModelSerializer

    # 列表序列化器(用于列表展示)
    list_serializer_class = OnAirOrderDetailModelListSerializer

    # 创建序列化器
    create_serializer_class = OnAirOrderDetailModelCreateSerializer

    # 更新序列化器
    update_serializer_class = OnAirOrderDetailModelUpdateSerializer

    # 过滤字段(支持精确查询)
    filter_fields = [
        "id",
        "order_id",
        "position_id",
        "roadline_id",
        "roadline_company_id",
        "plan_vehicle_id",
        "act_vehicle_id",
        "composite_media_type_id",
        "base_media_type_id",
        "execution_status",
        "enabled_mark",
        "delete_mark",
    ]

    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        "id",
        "order_id",
        "position_id",
        "roadline_id",
        "roadline_company_id",
        "plan_vehicle_id",
        "act_vehicle_id",
        "composite_media_type_id",
        "base_media_type_id",
        "execution_status",
        "enabled_mark",
        "delete_mark",
    ]

    # 搜索字段(支持模糊查询)
    search_fields = ["roadline_name", "roadline_company_name", "plan_vehicle_no", "act_vehicle_no", "base_media_type_name", "composite_media_type_name"]

    # 排序字段
    ordering_fields = [
        "create_datetime",
        "update_datetime",
        "act_on_air_datetime",
        "execution_status",
    ]

    # 默认排序
    ordering = ["-create_datetime"]
