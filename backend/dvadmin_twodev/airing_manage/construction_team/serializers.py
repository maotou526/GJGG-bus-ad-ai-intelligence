"""
Description: 施工团队序列化器
Version: 1.0
Autor: AI Assistant
Date: 2026-03-17
LastEditors:
LastEditTime: 2026-03-17
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import ConstructionTeamModel


class ConstructionTeamModelSerializer(CustomModelSerializer):
    """
    施工团队序列化器

    功能说明:
    - 提供施工团队数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer, 获得审计字段自动填充功能
    """

    # 团队类型显示名称
    team_type_display = serializers.SerializerMethodField()

    class Meta:
        model = ConstructionTeamModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "team_no": {"required": True, "allow_null": False, "allow_blank": False},
            "team_name": {"required": True, "allow_null": False, "allow_blank": False},
            "team_type": {"required": True, "allow_null": False},
            "contact_phone": {"required": False, "allow_null": True, "allow_blank": True},
            "remark": {"required": False, "allow_null": True, "allow_blank": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_team_type_display(self, obj):
        """团队类型显示名称"""
        type_map = {
            1: "自营团队",
            2: "代理商团队",
        }
        return type_map.get(obj.team_type, "未知")


class ConstructionTeamModelCreateSerializer(ConstructionTeamModelSerializer):
    """
    施工团队创建序列化器

    功能说明:
    - 专门用于创建新施工团队时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(ConstructionTeamModelSerializer.Meta):
        extra_kwargs = {
            **ConstructionTeamModelSerializer.Meta.extra_kwargs,
            "team_no": {"required": True, "allow_null": False, "allow_blank": False},
            "team_name": {"required": True, "allow_null": False, "allow_blank": False},
            "team_type": {"required": True, "allow_null": False},
        }


class ConstructionTeamModelUpdateSerializer(ConstructionTeamModelSerializer):
    """
    施工团队更新序列化器

    功能说明:
    - 专门用于更新现有施工团队时的数据验证
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(ConstructionTeamModelSerializer.Meta):
        read_only_fields = ["id", "create_datetime", "update_datetime", "team_no"]


class ConstructionTeamModelListSerializer(ConstructionTeamModelSerializer):
    """
    施工团队列表序列化器

    功能说明:
    - 专门用于施工团队列表显示, 优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量, 提高响应速度
    - 所有字段为只读, 确保数据安全
    """

    class Meta:
        model = ConstructionTeamModel
        fields = [
            "id",
            "team_no",
            "team_name",
            "team_type",
            "team_type_display",
            "contact_phone",
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
