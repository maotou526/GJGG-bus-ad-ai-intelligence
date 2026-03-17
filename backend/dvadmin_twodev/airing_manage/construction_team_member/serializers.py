"""
Description: 施工团队成员序列化器
Version: 1.0
Autor: AI Assistant
Date: 2026-03-17
LastEditors:
LastEditTime: 2026-03-17
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import ConstructionTeamMemberModel


class ConstructionTeamMemberModelSerializer(CustomModelSerializer):
    """
    施工团队成员序列化器

    功能说明:
    - 提供施工团队成员数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer, 获得审计字段自动填充功能
    """

    # 成员角色显示名称
    member_role_display = serializers.SerializerMethodField()

    # 成员状态显示名称
    member_status_display = serializers.SerializerMethodField()

    class Meta:
        model = ConstructionTeamMemberModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "team_id": {"required": True, "allow_null": False},
            "user_id": {"required": True, "allow_null": False, "allow_blank": False},
            "user_name": {"required": False, "allow_null": True, "allow_blank": True},
            "member_role": {"required": True, "allow_null": False},
            "id_card": {"required": False, "allow_null": True, "allow_blank": True},
            "phone": {"required": False, "allow_null": True, "allow_blank": True},
            "qualification": {"required": False, "allow_null": True, "allow_blank": True},
            "work_years": {"required": False, "allow_null": True},
            "join_time": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "member_status": {"required": False, "allow_null": False},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_member_role_display(self, obj):
        """成员角色显示名称"""
        role_map = {
            1: "负责人",
            2: "成员",
        }
        return role_map.get(obj.member_role, "未知")

    def get_member_status_display(self, obj):
        """成员状态显示名称"""
        status_map = {
            1: "在职",
            2: "离职",
        }
        return status_map.get(obj.member_status, "未知")


class ConstructionTeamMemberModelCreateSerializer(ConstructionTeamMemberModelSerializer):
    """
    施工团队成员创建序列化器

    功能说明:
    - 专门用于创建新施工团队成员时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(ConstructionTeamMemberModelSerializer.Meta):
        extra_kwargs = {
            **ConstructionTeamMemberModelSerializer.Meta.extra_kwargs,
            "team_id": {"required": True, "allow_null": False},
            "user_id": {"required": True, "allow_null": False, "allow_blank": False},
            "member_role": {"required": True, "allow_null": False},
        }


class ConstructionTeamMemberModelUpdateSerializer(ConstructionTeamMemberModelSerializer):
    """
    施工团队成员更新序列化器

    功能说明:
    - 专门用于更新现有施工团队成员时的数据验证
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(ConstructionTeamMemberModelSerializer.Meta):
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class ConstructionTeamMemberModelListSerializer(ConstructionTeamMemberModelSerializer):
    """
    施工团队成员列表序列化器

    功能说明:
    - 专门用于施工团队成员列表显示, 优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量, 提高响应速度
    - 所有字段为只读, 确保数据安全
    """

    class Meta:
        model = ConstructionTeamMemberModel
        fields = [
            "id",
            "team_id",
            "user_id",
            "user_name",
            "member_role",
            "member_role_display",
            "id_card",
            "phone",
            "qualification",
            "work_years",
            "join_time",
            "member_status",
            "member_status_display",
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
            "enabled_mark",
            "delete_mark",
        ]
        read_only_fields = fields
