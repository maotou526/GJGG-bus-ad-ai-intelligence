"""
Description: 上刊施工文件视图
Version: 1.0
"""
from dvadmin.utils.viewset import CustomModelViewSet

from .models import OnAirFileModel
from .serializers import (
    OnAirFileModelSerializer,
    OnAirFileModelCreateSerializer,
    OnAirFileModelUpdateSerializer,
    OnAirFileModelListSerializer,
)


class OnAirFileModelViewSet(CustomModelViewSet):
    """
    上刊施工文件管理视图集

    功能说明:
    - 提供上刊施工文件的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作

    标准DRF接口:
    - GET /api/OnAirFileModelViewSet/ - 获取施工文件列表
    - POST /api/OnAirFileModelViewSet/ - 创建施工文件
    - PUT /api/OnAirFileModelViewSet/{id}/ - 更新施工文件
    - PATCH /api/OnAirFileModelViewSet/{id}/ - 部分更新施工文件
    - DELETE /api/OnAirFileModelViewSet/{id}/ - 删除施工文件
    """

    # 查询集
    queryset = OnAirFileModel.objects.all()

    # 默认序列化器(用于查询详情)
    serializer_class = OnAirFileModelSerializer

    # 列表序列化器(用于列表展示)
    list_serializer_class = OnAirFileModelListSerializer

    # 创建序列化器
    create_serializer_class = OnAirFileModelCreateSerializer

    # 更新序列化器
    update_serializer_class = OnAirFileModelUpdateSerializer

    # 过滤字段(支持精确查询)
    filter_fields = [
        "order_detail_id",
        "file_type",
    ]

    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        "order_detail_id",
        "file_type",
    ]

    # 搜索字段(支持模糊查询)
    search_fields = ["file_path", "gps_location"]

    # 排序字段
    ordering_fields = [
        "create_datetime",
        "update_datetime",
        "file_type",
        "capture_time",
        "upload_time",
    ]

    # 默认排序
    ordering = ["-create_datetime"]
