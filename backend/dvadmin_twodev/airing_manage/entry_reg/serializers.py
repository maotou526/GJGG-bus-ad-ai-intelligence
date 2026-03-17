"""
Description: 进场登记序列化器
Version: 1.0
"""
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import EntryRegModel


class EntryRegModelSerializer(CustomModelSerializer):
    """
    进场登记序列化器

    功能说明:
    - 提供进场登记数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer, 获得审计字段自动填充功能
    """

    # 任务类型显示名称
    task_type_display = serializers.SerializerMethodField()

    class Meta:
        model = EntryRegModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]

    def get_task_type_display(self, obj):
        """任务类型显示名称"""
        type_map = {
            1: "上刊",
            2: "下刊",
        }
        return type_map.get(obj.task_type, "未知")


class EntryRegModelCreateSerializer(EntryRegModelSerializer):
    """
    进场登记创建序列化器

    功能说明:
    - 专门用于创建新进场登记记录时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    """

    class Meta(EntryRegModelSerializer.Meta):
        extra_kwargs = {
            "task_type": {"required": True, "allow_null": False},
            "task_id": {"required": True, "allow_null": False, "allow_blank": False},
            "team_vehicle_id": {"required": True, "allow_null": False, "allow_blank": False},
            "leader_id": {"required": True, "allow_null": False, "allow_blank": False},
            "register_time": {"required": True, "allow_null": False},
        }


class EntryRegModelUpdateSerializer(EntryRegModelSerializer):
    """
    进场登记更新序列化器

    功能说明:
    - 专门用于更新现有进场登记记录时的数据验证
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    """

    class Meta(EntryRegModelSerializer.Meta):
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class EntryRegModelListSerializer(EntryRegModelSerializer):
    """
    进场登记列表序列化器

    功能说明:
    - 专门用于进场登记列表显示, 优化性能
    - 只包含列表展示需要的核心字段
    - 所有字段为只读, 确保数据安全
    """

    class Meta:
        model = EntryRegModel
        fields = [
            "id",
            "task_type",
            "task_type_display",
            "task_id",
            "team_vehicle_id",
            "plate_no",
            "leader_id",
            "leader_name",
            "leader_phone",
            "expected_entry_time",
            "expected_exit_time",
            "qr_code_image",
            "register_time",
            "register_user_id",
            "remark",
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
            "enabled_mark",
            "delete_mark",
        ]
        read_only_fields = fields
