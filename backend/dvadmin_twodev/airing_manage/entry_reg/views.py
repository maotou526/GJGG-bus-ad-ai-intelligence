"""
Description: 进场登记视图
Version: 1.0
"""
from dvadmin.utils.viewset import CustomModelViewSet

from .models import EntryRegModel
from .serializers import (
    EntryRegModelSerializer,
    EntryRegModelCreateSerializer,
    EntryRegModelUpdateSerializer,
    EntryRegModelListSerializer,
)


class EntryRegModelViewSet(CustomModelViewSet):
    """
    进场登记管理视图集

    功能说明:
    - 提供进场登记的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作

    标准DRF接口:
    - GET /api/EntryRegModelViewSet/ - 获取进场登记列表
    - POST /api/EntryRegModelViewSet/ - 创建进场登记
    - PUT /api/EntryRegModelViewSet/{id}/ - 更新进场登记
    - PATCH /api/EntryRegModelViewSet/{id}/ - 部分更新进场登记
    - DELETE /api/EntryRegModelViewSet/{id}/ - 删除进场登记
    """

    # 查询集
    queryset = EntryRegModel.objects.all()

    # 默认序列化器(用于查询详情)
    serializer_class = EntryRegModelSerializer

    # 列表序列化器(用于列表展示)
    list_serializer_class = EntryRegModelListSerializer

    # 创建序列化器
    create_serializer_class = EntryRegModelCreateSerializer

    # 更新序列化器
    update_serializer_class = EntryRegModelUpdateSerializer

    # 过滤字段(支持精确查询)
    filter_fields = [
        "task_type",
        "task_id",
        "team_vehicle_id",
        "plate_no",
    ]

    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        "task_type",
        "task_id",
        "team_vehicle_id",
        "plate_no",
    ]

    # 搜索字段(支持模糊查询)
    search_fields = ["plate_no", "leader_name"]

    # 排序字段
    ordering_fields = [
        "create_datetime",
        "update_datetime",
        "task_type",
        "register_time",
    ]

    # 默认排序
    ordering = ["-create_datetime"]
