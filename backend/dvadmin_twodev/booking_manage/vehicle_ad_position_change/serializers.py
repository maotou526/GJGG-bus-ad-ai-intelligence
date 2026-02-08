"""
Description: 车位广告变更历史序列化器
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors:
LastEditTime: 2025-01-XX
"""

from rest_framework import serializers

from dvadmin.utils.serializers import CustomModelSerializer
from .models import VehicleAdPositionChangeModel


class VehicleAdPositionChangeModelSerializer(CustomModelSerializer):
    """
    车位广告变更历史序列化器

    功能说明:
    - 提供车位广告变更历史数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、查询等操作
    """

    class Meta:
        model = VehicleAdPositionChangeModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "booking_order_id": {"required": True, "allow_null": False},
            "booking_detail_id": {"required": False, "allow_null": True},
            "action_type": {"required": True, "allow_null": False},
            "position_id": {"required": False, "allow_null": True},
            "roadline_id": {"required": False, "allow_null": True},
            "roadline_name": {"required": False, "allow_null": True, "allow_blank": True},
            "roadline_company_id": {"required": False, "allow_null": True},
            "roadline_company_name": {"required": False, "allow_null": True, "allow_blank": True},
            "vehicle_id": {"required": False, "allow_null": True},
            "vehicle_no": {"required": False, "allow_null": True, "allow_blank": True},
            "resource_id": {"required": False, "allow_null": True},
            "before_data": {"required": False, "allow_null": True},
            "after_data": {"required": False, "allow_null": True},
            "change_reason": {"required": False, "allow_null": True, "allow_blank": True},
            "change_node": {"required": True, "allow_null": False, "allow_blank": False},
            "operator_id": {"required": False, "allow_null": True},
            "operation_time": {
                "required": True,
                "allow_null": False,
                "format": "%Y-%m-%d %H:%M:%S",
                "input_formats": ["%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"],
            },
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def validate_action_type(self, value):
        """验证操作类型"""
        if value not in [1, 2, 3]:
            raise serializers.ValidationError("操作类型只能是：1=新增车位, 2=删除车位, 3=修改车位")
        return value

    def validate_change_node(self, value):
        """验证变更节点"""
        if not value:
            raise serializers.ValidationError("变更节点不能为空")
        # 文档定义的业务含义由前端/调用方控制，这里仅做非空校验
        return value


class VehicleAdPositionChangeModelCreateSerializer(VehicleAdPositionChangeModelSerializer):
    """
    车位广告变更历史创建序列化器

    功能说明:
    - 专门用于创建车位广告变更历史记录时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(VehicleAdPositionChangeModelSerializer.Meta):
        extra_kwargs = {
            **VehicleAdPositionChangeModelSerializer.Meta.extra_kwargs,
            "booking_order_id": {"required": True, "allow_null": False},
            "action_type": {"required": True, "allow_null": False},
            "change_node": {"required": True, "allow_null": False, "allow_blank": False},
            "operation_time": {"required": True, "allow_null": False},
        }


class VehicleAdPositionChangeModelListSerializer(VehicleAdPositionChangeModelSerializer):
    """
    车位广告变更历史列表序列化器

    功能说明:
    - 专门用于车位广告变更历史列表显示, 优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量, 提高响应速度
    - 所有字段为只读, 确保数据安全
    """

    class Meta:
        model = VehicleAdPositionChangeModel
        fields = [
            "id",
            "booking_order_id",
            "booking_detail_id",
            "action_type",
            "position_id",
            "roadline_id",
            "roadline_name",
            "roadline_company_id",
            "roadline_company_name",
            "vehicle_id",
            "vehicle_no",
            "resource_id",
            "change_node",
            "operation_time",
            "change_reason",
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
            "enabled_mark",
            "delete_mark",
        ]
        read_only_fields = fields


