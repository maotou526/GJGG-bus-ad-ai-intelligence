"""
Description: 上刊施工人员序列化器
Version: 1.0
"""
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import OnAirWorkerModel


class OnAirWorkerModelSerializer(CustomModelSerializer):
    """
    上刊施工人员序列化器

    功能说明:
    - 提供上刊施工人员数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer, 获得审计字段自动填充功能
    """

    # 人员角色显示名称
    person_role_display = serializers.SerializerMethodField()

    class Meta:
        model = OnAirWorkerModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]

    def get_person_role_display(self, obj):
        """人员角色显示名称"""
        role_map = {
            1: "施工负责人",
            2: "施工人员",
        }
        return role_map.get(obj.person_role, "未知")


class OnAirWorkerModelCreateSerializer(OnAirWorkerModelSerializer):
    """
    上刊施工人员创建序列化器

    功能说明:
    - 专门用于创建新施工人员记录时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    """

    class Meta(OnAirWorkerModelSerializer.Meta):
        extra_kwargs = {
            "order_id": {"required": True, "allow_null": False},
            "user_id": {"required": True, "allow_null": False, "allow_blank": False},
            "person_role": {"required": True, "allow_null": False},
        }


class OnAirWorkerModelUpdateSerializer(OnAirWorkerModelSerializer):
    """
    上刊施工人员更新序列化器

    功能说明:
    - 专门用于更新现有施工人员记录时的数据验证
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    """

    class Meta(OnAirWorkerModelSerializer.Meta):
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OnAirWorkerModelListSerializer(OnAirWorkerModelSerializer):
    """
    上刊施工人员列表序列化器

    功能说明:
    - 专门用于施工人员列表显示, 优化性能
    - 只包含列表展示需要的核心字段
    - 所有字段为只读, 确保数据安全
    """

    class Meta:
        model = OnAirWorkerModel
        fields = [
            "id",
            "order_id",
            "user_id",
            "user_name",
            "team_id",
            "team_name",
            "person_role",
            "person_role_display",
            "expected_entry_time",
            "expected_exit_time",
            "actual_entry_time",
            "actual_exit_time",
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
            "enabled_mark",
            "delete_mark",
        ]
        read_only_fields = fields
