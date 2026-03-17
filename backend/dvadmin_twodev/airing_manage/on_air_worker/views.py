"""
Description: 上刊施工人员视图
Version: 1.0
"""
from dvadmin.utils.viewset import CustomModelViewSet

from .models import OnAirWorkerModel
from .serializers import (
    OnAirWorkerModelSerializer,
    OnAirWorkerModelCreateSerializer,
    OnAirWorkerModelUpdateSerializer,
    OnAirWorkerModelListSerializer,
)


class OnAirWorkerModelViewSet(CustomModelViewSet):
    """
    上刊施工人员管理视图集

    功能说明:
    - 提供上刊施工人员的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作

    标准DRF接口:
    - GET /api/OnAirWorkerModelViewSet/ - 获取施工人员列表
    - POST /api/OnAirWorkerModelViewSet/ - 创建施工人员
    - PUT /api/OnAirWorkerModelViewSet/{id}/ - 更新施工人员
    - PATCH /api/OnAirWorkerModelViewSet/{id}/ - 部分更新施工人员
    - DELETE /api/OnAirWorkerModelViewSet/{id}/ - 删除施工人员
    """

    # 查询集
    queryset = OnAirWorkerModel.objects.all()

    # 默认序列化器(用于查询详情)
    serializer_class = OnAirWorkerModelSerializer

    # 列表序列化器(用于列表展示)
    list_serializer_class = OnAirWorkerModelListSerializer

    # 创建序列化器
    create_serializer_class = OnAirWorkerModelCreateSerializer

    # 更新序列化器
    update_serializer_class = OnAirWorkerModelUpdateSerializer

    # 过滤字段(支持精确查询)
    filter_fields = [
        "order_id",
        "user_id",
        "team_id",
        "person_role",
    ]

    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        "order_id",
        "user_id",
        "team_id",
        "person_role",
    ]

    # 搜索字段(支持模糊查询)
    search_fields = ["user_name", "team_name"]

    # 排序字段
    ordering_fields = [
        "create_datetime",
        "update_datetime",
        "person_role",
    ]

    # 默认排序
    ordering = ["-create_datetime"]
