"""
Description: 上刊订单序列化器
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import OnAirOrderModel


class OnAirOrderModelSerializer(CustomModelSerializer):
    """
    上刊订单序列化器

    功能说明:
    - 提供上刊订单数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer, 获得审计字段自动填充功能
    """

    # 订单状态显示名称
    order_status_display = serializers.SerializerMethodField()

    class Meta:
        model = OnAirOrderModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "order_no": {"required": True, "allow_null": False, "allow_blank": False},
            "booking_order_id": {"required": True, "allow_null": False},
            "customer_name": {"required": False, "allow_null": True, "allow_blank": True},
            "booking_start_date": {"required": True, "allow_null": False, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "booking_end_date": {"required": True, "allow_null": False, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "order_status": {"required": True, "allow_null": False},
            "approved_time": {"required": False, "allow_null": True, "format": "%Y-%m-%d %H:%M:%S", "input_formats": ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]},
            "remark": {"required": False, "allow_null": True, "allow_blank": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_order_status_display(self, obj):
        """订单状态显示名称"""
        status_map = {
            1: "草稿",
            2: "待审批",
            3: "审批中",
            4: "已通过",
            5: "施工中",
            6: "已完成",
            7: "已驳回",
        }
        return status_map.get(obj.order_status, "未知")

    def validate_order_status(self, value):
        """验证订单状态"""
        if value not in [1, 2, 3, 4, 5, 6, 7]:
            raise serializers.ValidationError("订单状态只能是：1=草稿, 2=待审批, 3=审批中, 4=已通过, 5=施工中, 6=已完成, 7=已驳回")
        return value

    def validate(self, attrs):
        """整体验证"""
        booking_start_date = attrs.get("booking_start_date")
        booking_end_date = attrs.get("booking_end_date")
        if booking_start_date and booking_end_date and booking_start_date > booking_end_date:
            raise serializers.ValidationError("投放开始日期不能晚于投放结束日期")
        return attrs


class OnAirOrderModelCreateSerializer(OnAirOrderModelSerializer):
    """
    上刊订单创建序列化器

    功能说明:
    - 专门用于创建新上刊订单时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(OnAirOrderModelSerializer.Meta):
        extra_kwargs = {
            **OnAirOrderModelSerializer.Meta.extra_kwargs,
            "order_no": {"required": True, "allow_null": False, "allow_blank": False},
            "booking_order_id": {"required": True, "allow_null": False},
            "booking_start_date": {"required": True, "allow_null": False},
            "booking_end_date": {"required": True, "allow_null": False},
            "order_status": {"required": True, "allow_null": False},
        }

    def create(self, validated_data):
        """创建上刊订单时自动填充部分冗余字段"""
        booking_order_id = validated_data.get("booking_order_id")
        if booking_order_id and not validated_data.get("customer_name"):
            try:
                if hasattr(booking_order_id, "customer_id") and hasattr(booking_order_id.customer_id, "customer_name"):
                    validated_data["customer_name"] = booking_order_id.customer_id.customer_name
            except Exception:
                pass

        return super().create(validated_data)


class OnAirOrderModelUpdateSerializer(OnAirOrderModelSerializer):
    """
    上刊订单更新序列化器

    功能说明:
    - 专门用于更新现有上刊订单时的数据验证
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(OnAirOrderModelSerializer.Meta):
        read_only_fields = ["id", "create_datetime", "update_datetime", "order_no"]

    def update(self, instance, validated_data):
        """更新时自动填充部分冗余字段"""
        booking_order_id = validated_data.get("booking_order_id")
        if booking_order_id and booking_order_id != instance.booking_order_id:
            try:
                if hasattr(booking_order_id, "customer_id") and hasattr(booking_order_id.customer_id, "customer_name"):
                    validated_data["customer_name"] = booking_order_id.customer_id.customer_name
            except Exception:
                pass

        return super().update(instance, validated_data)


class OnAirOrderModelListSerializer(OnAirOrderModelSerializer):
    """
    上刊订单列表序列化器

    功能说明:
    - 专门用于上刊订单列表显示, 优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量, 提高响应速度
    - 所有字段为只读, 确保数据安全
    """

    class Meta:
        model = OnAirOrderModel
        fields = [
            # 基础信息
            "id",
            "order_no",
            "booking_order_id",
            "customer_name",
            # 时间信息
            "booking_start_date",
            "booking_end_date",
            "approved_time",
            # 状态信息
            "order_status",
            "order_status_display",
            # 备注
            "remark",
            # 审计字段
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
            "enabled_mark",
            "delete_mark",
        ]
        read_only_fields = fields
