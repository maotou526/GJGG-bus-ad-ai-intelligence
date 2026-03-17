"""
Description: 上刊施工文件序列化器
Version: 1.0
"""
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import OnAirFileModel


class OnAirFileModelSerializer(CustomModelSerializer):
    """
    上刊施工文件序列化器

    功能说明:
    - 提供上刊施工文件数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer, 获得审计字段自动填充功能
    """

    # 文件类型显示名称
    file_type_display = serializers.SerializerMethodField()

    class Meta:
        model = OnAirFileModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]

    def get_file_type_display(self, obj):
        """文件类型显示名称"""
        type_map = {
            1: "施工前",
            2: "施工中",
            3: "完工后",
        }
        return type_map.get(obj.file_type, "未知")


class OnAirFileModelCreateSerializer(OnAirFileModelSerializer):
    """
    上刊施工文件创建序列化器

    功能说明:
    - 专门用于创建新施工文件记录时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    """

    class Meta(OnAirFileModelSerializer.Meta):
        extra_kwargs = {
            "order_detail_id": {"required": True, "allow_null": False},
            "file_type": {"required": True, "allow_null": False},
            "file_path": {"required": True, "allow_null": False, "allow_blank": False},
            "capture_time": {"required": True, "allow_null": False},
            "upload_time": {"required": True, "allow_null": False},
        }


class OnAirFileModelUpdateSerializer(OnAirFileModelSerializer):
    """
    上刊施工文件更新序列化器

    功能说明:
    - 专门用于更新现有施工文件记录时的数据验证
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    """

    class Meta(OnAirFileModelSerializer.Meta):
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OnAirFileModelListSerializer(OnAirFileModelSerializer):
    """
    上刊施工文件列表序列化器

    功能说明:
    - 专门用于施工文件列表显示, 优化性能
    - 只包含列表展示需要的核心字段
    - 所有字段为只读, 确保数据安全
    """

    class Meta:
        model = OnAirFileModel
        fields = [
            "id",
            "order_detail_id",
            "file_type",
            "file_type_display",
            "file_path",
            "capture_time",
            "gps_location",
            "constructor_id",
            "uploader_id",
            "upload_time",
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
            "enabled_mark",
            "delete_mark",
        ]
        read_only_fields = fields
