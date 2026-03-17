"""
Description: 施工团队车辆序列化器
Version: 1.0
Autor: AI Assistant
Date: 2026-03-17
LastEditors:
LastEditTime: 2026-03-17
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import ConstructionTeamVehicleModel


class ConstructionTeamVehicleModelSerializer(CustomModelSerializer):
    """
    施工团队车辆序列化器

    功能说明:
    - 提供施工团队车辆数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer, 获得审计字段自动填充功能
    """

    # 车辆状态显示名称
    vehicle_status_display = serializers.SerializerMethodField()

    class Meta:
        model = ConstructionTeamVehicleModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "team_id": {"required": True, "allow_null": False},
            "vehicle_no": {"required": True, "allow_null": False, "allow_blank": False},
            "plate_no": {"required": True, "allow_null": False, "allow_blank": False},
            "vehicle_type": {"required": False, "allow_null": True, "allow_blank": True},
            "leader_id": {"required": True, "allow_null": False, "allow_blank": False},
            "leader_name": {"required": False, "allow_null": True, "allow_blank": True},
            "leader_phone": {"required": False, "allow_null": True, "allow_blank": True},
            "vehicle_status": {"required": False, "allow_null": False},
            "remark": {"required": False, "allow_null": True, "allow_blank": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_vehicle_status_display(self, obj):
        """车辆状态显示名称"""
        status_map = {
            1: "正常",
            2: "维修中",
            3: "停用",
        }
        return status_map.get(obj.vehicle_status, "未知")


class ConstructionTeamVehicleModelCreateSerializer(ConstructionTeamVehicleModelSerializer):
    """
    施工团队车辆创建序列化器

    功能说明:
    - 专门用于创建新施工团队车辆时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(ConstructionTeamVehicleModelSerializer.Meta):
        extra_kwargs = {
            **ConstructionTeamVehicleModelSerializer.Meta.extra_kwargs,
            "team_id": {"required": True, "allow_null": False},
            "vehicle_no": {"required": True, "allow_null": False, "allow_blank": False},
            "plate_no": {"required": True, "allow_null": False, "allow_blank": False},
            "leader_id": {"required": True, "allow_null": False, "allow_blank": False},
        }


class ConstructionTeamVehicleModelUpdateSerializer(ConstructionTeamVehicleModelSerializer):
    """
    施工团队车辆更新序列化器

    功能说明:
    - 专门用于更新现有施工团队车辆时的数据验证
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(ConstructionTeamVehicleModelSerializer.Meta):
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class ConstructionTeamVehicleModelListSerializer(ConstructionTeamVehicleModelSerializer):
    """
    施工团队车辆列表序列化器

    功能说明:
    - 专门用于施工团队车辆列表显示, 优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量, 提高响应速度
    - 所有字段为只读, 确保数据安全
    """

    class Meta:
        model = ConstructionTeamVehicleModel
        fields = [
            "id",
            "team_id",
            "vehicle_no",
            "plate_no",
            "vehicle_type",
            "leader_id",
            "leader_name",
            "leader_phone",
            "vehicle_status",
            "vehicle_status_display",
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
