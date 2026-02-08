'''
Description: 上刊订单视图
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from dvadmin.utils.viewset import CustomModelViewSet

from .models import OnAirOrderModel
from .serializers import (
    OnAirOrderModelSerializer,
    OnAirOrderModelCreateSerializer,
    OnAirOrderModelUpdateSerializer,
    OnAirOrderModelListSerializer,
)


class OnAirOrderModelViewSet(CustomModelViewSet):
    """
    上刊订单管理视图集

    功能说明:
    - 提供上刊订单的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作

    标准DRF接口:
    - GET /api/OnAirOrderModelViewSet/ - 获取上刊订单列表
    - POST /api/OnAirOrderModelViewSet/ - 创建上刊订单
    - PUT /api/OnAirOrderModelViewSet/{id}/ - 更新上刊订单
    - PATCH /api/OnAirOrderModelViewSet/{id}/ - 部分更新上刊订单
    - DELETE /api/OnAirOrderModelViewSet/{id}/ - 删除上刊订单
    """

    # 查询集
    queryset = OnAirOrderModel.objects.all()

    # 默认序列化器(用于查询详情)
    serializer_class = OnAirOrderModelSerializer

    # 列表序列化器(用于列表展示)
    list_serializer_class = OnAirOrderModelListSerializer

    # 创建序列化器
    create_serializer_class = OnAirOrderModelCreateSerializer

    # 更新序列化器
    update_serializer_class = OnAirOrderModelUpdateSerializer

    # 过滤字段(支持精确查询)
    filter_fields = [
        "id",
        "order_no",
        "booking_order_id",
        "customer_name",
        "order_status",
        "enabled_mark",
        "delete_mark",
    ]

    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        "id",
        "order_no",
        "booking_order_id",
        "customer_name",
        "order_status",
        "enabled_mark",
        "delete_mark",
    ]

    # 搜索字段(支持模糊查询)
    search_fields = ["order_no", "customer_name"]

    # 排序字段
    ordering_fields = [
        "create_datetime",
        "update_datetime",
        "booking_start_date",
        "booking_end_date",
        "approved_time",
        "order_status",
    ]

    # 默认排序
    ordering = ["-create_datetime"]
