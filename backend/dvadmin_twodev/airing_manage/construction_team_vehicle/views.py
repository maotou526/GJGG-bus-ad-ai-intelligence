'''
Description: 施工团队车辆视图
Version: 1.0
Autor: AI Assistant
Date: 2026-03-17
LastEditors:
LastEditTime: 2026-03-17
'''
from dvadmin.utils.viewset import CustomModelViewSet

from .models import ConstructionTeamVehicleModel
from .serializers import (
    ConstructionTeamVehicleModelSerializer,
    ConstructionTeamVehicleModelCreateSerializer,
    ConstructionTeamVehicleModelUpdateSerializer,
    ConstructionTeamVehicleModelListSerializer,
)


class ConstructionTeamVehicleModelViewSet(CustomModelViewSet):
    """
    施工团队车辆管理视图集

    功能说明:
    - 提供施工团队车辆的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作

    标准DRF接口:
    - GET /api/ConstructionTeamVehicleModelViewSet/ - 获取施工团队车辆列表
    - POST /api/ConstructionTeamVehicleModelViewSet/ - 创建施工团队车辆
    - PUT /api/ConstructionTeamVehicleModelViewSet/{id}/ - 更新施工团队车辆
    - PATCH /api/ConstructionTeamVehicleModelViewSet/{id}/ - 部分更新施工团队车辆
    - DELETE /api/ConstructionTeamVehicleModelViewSet/{id}/ - 删除施工团队车辆
    """

    # 查询集
    queryset = ConstructionTeamVehicleModel.objects.all()

    # 默认序列化器(用于查询详情)
    serializer_class = ConstructionTeamVehicleModelSerializer

    # 列表序列化器(用于列表展示)
    list_serializer_class = ConstructionTeamVehicleModelListSerializer

    # 创建序列化器
    create_serializer_class = ConstructionTeamVehicleModelCreateSerializer

    # 更新序列化器
    update_serializer_class = ConstructionTeamVehicleModelUpdateSerializer

    # 过滤字段(支持精确查询)
    filter_fields = [
        "id",
        "team_id",
        "plate_no",
        "vehicle_status",
        "vehicle_type",
        "enabled_mark",
        "delete_mark",
    ]

    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        "id",
        "team_id",
        "plate_no",
        "vehicle_status",
        "vehicle_type",
        "enabled_mark",
        "delete_mark",
    ]

    # 搜索字段(支持模糊查询)
    search_fields = ["vehicle_no", "plate_no", "leader_name"]

    # 排序字段
    ordering_fields = [
        "create_datetime",
        "update_datetime",
        "vehicle_no",
        "plate_no",
        "vehicle_status",
    ]

    # 默认排序
    ordering = ["-create_datetime"]
