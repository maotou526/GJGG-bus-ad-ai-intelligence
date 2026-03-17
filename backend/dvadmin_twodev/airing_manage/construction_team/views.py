'''
Description: 施工团队视图
Version: 1.0
Autor: AI Assistant
Date: 2026-03-17
LastEditors:
LastEditTime: 2026-03-17
'''
from dvadmin.utils.viewset import CustomModelViewSet

from .models import ConstructionTeamModel
from .serializers import (
    ConstructionTeamModelSerializer,
    ConstructionTeamModelCreateSerializer,
    ConstructionTeamModelUpdateSerializer,
    ConstructionTeamModelListSerializer,
)


class ConstructionTeamModelViewSet(CustomModelViewSet):
    """
    施工团队管理视图集

    功能说明:
    - 提供施工团队的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作

    标准DRF接口:
    - GET /api/ConstructionTeamModelViewSet/ - 获取施工团队列表
    - POST /api/ConstructionTeamModelViewSet/ - 创建施工团队
    - PUT /api/ConstructionTeamModelViewSet/{id}/ - 更新施工团队
    - PATCH /api/ConstructionTeamModelViewSet/{id}/ - 部分更新施工团队
    - DELETE /api/ConstructionTeamModelViewSet/{id}/ - 删除施工团队
    """

    # 查询集
    queryset = ConstructionTeamModel.objects.all()

    # 默认序列化器(用于查询详情)
    serializer_class = ConstructionTeamModelSerializer

    # 列表序列化器(用于列表展示)
    list_serializer_class = ConstructionTeamModelListSerializer

    # 创建序列化器
    create_serializer_class = ConstructionTeamModelCreateSerializer

    # 更新序列化器
    update_serializer_class = ConstructionTeamModelUpdateSerializer

    # 过滤字段(支持精确查询)
    filter_fields = [
        "id",
        "team_no",
        "team_name",
        "team_type",
        "enabled_mark",
        "delete_mark",
    ]

    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        "id",
        "team_no",
        "team_name",
        "team_type",
        "enabled_mark",
        "delete_mark",
    ]

    # 搜索字段(支持模糊查询)
    search_fields = ["team_no", "team_name"]

    # 排序字段
    ordering_fields = [
        "create_datetime",
        "update_datetime",
        "team_no",
        "team_type",
    ]

    # 默认排序
    ordering = ["-create_datetime"]
