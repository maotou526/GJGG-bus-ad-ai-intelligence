'''
Description: 上刊材料视图
Version: 1.0
Autor: AI Assistant
Date: 2026-03-17
LastEditors:
LastEditTime: 2026-03-17
'''
from dvadmin.utils.viewset import CustomModelViewSet

from .models import OnAirMaterialModel
from .serializers import (
    OnAirMaterialModelSerializer,
    OnAirMaterialModelCreateSerializer,
    OnAirMaterialModelUpdateSerializer,
    OnAirMaterialModelListSerializer,
)


class OnAirMaterialModelViewSet(CustomModelViewSet):
    """
    上刊材料管理视图集

    功能说明:
    - 提供上刊材料的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作

    标准DRF接口:
    - GET /api/OnAirMaterialModelViewSet/ - 获取上刊材料列表
    - POST /api/OnAirMaterialModelViewSet/ - 创建上刊材料
    - PUT /api/OnAirMaterialModelViewSet/{id}/ - 更新上刊材料
    - PATCH /api/OnAirMaterialModelViewSet/{id}/ - 部分更新上刊材料
    - DELETE /api/OnAirMaterialModelViewSet/{id}/ - 删除上刊材料
    """

    # 查询集
    queryset = OnAirMaterialModel.objects.all()

    # 默认序列化器(用于查询详情)
    serializer_class = OnAirMaterialModelSerializer

    # 列表序列化器(用于列表展示)
    list_serializer_class = OnAirMaterialModelListSerializer

    # 创建序列化器
    create_serializer_class = OnAirMaterialModelCreateSerializer

    # 更新序列化器
    update_serializer_class = OnAirMaterialModelUpdateSerializer

    # 过滤字段(支持精确查询)
    filter_fields = [
        "id",
        "order_id",
        "material_category",
        "audit_status",
        "file_format",
        "is_required",
        "enabled_mark",
        "delete_mark",
    ]

    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        "id",
        "order_id",
        "material_category",
        "audit_status",
        "file_format",
        "is_required",
        "enabled_mark",
        "delete_mark",
    ]

    # 搜索字段(支持模糊查询)
    search_fields = ["file_name", "material_type_name"]

    # 排序字段
    ordering_fields = [
        "create_datetime",
        "update_datetime",
        "upload_time",
        "material_category",
        "audit_status",
    ]

    # 默认排序
    ordering = ["-create_datetime"]
