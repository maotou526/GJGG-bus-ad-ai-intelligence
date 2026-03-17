'''
Description: 施工团队成员视图
Version: 1.0
Autor: AI Assistant
Date: 2026-03-17
LastEditors:
LastEditTime: 2026-03-17
'''
from dvadmin.utils.viewset import CustomModelViewSet

from .models import ConstructionTeamMemberModel
from .serializers import (
    ConstructionTeamMemberModelSerializer,
    ConstructionTeamMemberModelCreateSerializer,
    ConstructionTeamMemberModelUpdateSerializer,
    ConstructionTeamMemberModelListSerializer,
)


class ConstructionTeamMemberModelViewSet(CustomModelViewSet):
    """
    施工团队成员管理视图集

    功能说明:
    - 提供施工团队成员的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作

    标准DRF接口:
    - GET /api/ConstructionTeamMemberModelViewSet/ - 获取施工团队成员列表
    - POST /api/ConstructionTeamMemberModelViewSet/ - 创建施工团队成员
    - PUT /api/ConstructionTeamMemberModelViewSet/{id}/ - 更新施工团队成员
    - PATCH /api/ConstructionTeamMemberModelViewSet/{id}/ - 部分更新施工团队成员
    - DELETE /api/ConstructionTeamMemberModelViewSet/{id}/ - 删除施工团队成员
    """

    # 查询集
    queryset = ConstructionTeamMemberModel.objects.all()

    # 默认序列化器(用于查询详情)
    serializer_class = ConstructionTeamMemberModelSerializer

    # 列表序列化器(用于列表展示)
    list_serializer_class = ConstructionTeamMemberModelListSerializer

    # 创建序列化器
    create_serializer_class = ConstructionTeamMemberModelCreateSerializer

    # 更新序列化器
    update_serializer_class = ConstructionTeamMemberModelUpdateSerializer

    # 过滤字段(支持精确查询)
    filter_fields = [
        "id",
        "team_id",
        "user_id",
        "member_role",
        "member_status",
        "enabled_mark",
        "delete_mark",
    ]

    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        "id",
        "team_id",
        "user_id",
        "member_role",
        "member_status",
        "enabled_mark",
        "delete_mark",
    ]

    # 搜索字段(支持模糊查询)
    search_fields = ["user_name", "phone"]

    # 排序字段
    ordering_fields = [
        "create_datetime",
        "update_datetime",
        "member_role",
        "member_status",
        "join_time",
        "work_years",
    ]

    # 默认排序
    ordering = ["-create_datetime"]
