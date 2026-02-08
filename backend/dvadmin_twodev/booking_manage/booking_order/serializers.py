"""
Description: 预订订单序列化器
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import BookingOrderModel


class BookingOrderModelSerializer(CustomModelSerializer):
    """
    预订订单序列化器

    功能说明:
    - 提供预订订单数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer,获得审计字段自动填充功能
    """

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()

    # 计算字段 - 预订单类型显示名称
    booking_type_display = serializers.SerializerMethodField()

    # 计算字段 - 预订单状态显示名称
    booking_status_display = serializers.SerializerMethodField()

    class Meta:
        model = BookingOrderModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "booking_no": {"required": True, "allow_null": False, "allow_blank": False},
            "customer_id": {"required": True, "allow_null": False},
            "customer_name": {"required": False, "allow_null": True, "allow_blank": True},
            "booking_type": {"required": True, "allow_null": False},
            "original_booking_id": {"required": False, "allow_null": True},
            "booking_status": {"required": True, "allow_null": False},
            "ad_content": {"required": False, "allow_null": True, "allow_blank": True},
            "start_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "end_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "duration_days": {"required": False, "allow_null": True},
            "total_amount": {"required": False, "allow_null": True, "max_digits": 15, "decimal_places": 2},
            "paid_amount": {"required": False, "allow_null": True, "max_digits": 15, "decimal_places": 2},
            "approved_time": {"required": False, "allow_null": True, "format": "%Y-%m-%d %H:%M:%S", "input_formats": ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]},
            "submitter_id": {"required": False, "allow_null": True},
            "submit_time": {"required": False, "allow_null": True, "format": "%Y-%m-%d %H:%M:%S", "input_formats": ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]},
            "current_approval_node": {"required": False, "allow_null": True},
            "reject_reason": {"required": False, "allow_null": True, "allow_blank": True},
            "reject_node": {"required": False, "allow_null": True},
            "reject_user_id": {"required": False, "allow_null": True},
            "reject_time": {"required": False, "allow_null": True, "format": "%Y-%m-%d %H:%M:%S", "input_formats": ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]},
            "remark": {"required": False, "allow_null": True, "allow_blank": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0

    # 当前审批节点显示名称
    current_approval_node_display = serializers.SerializerMethodField()

    def get_booking_type_display(self, obj):
        """预订单类型显示名称"""
        type_map = {
            1: "新预订",
            2: "续期",
            3: "变更",
            4: "重新发起",
        }
        return type_map.get(obj.booking_type, "未知")

    def get_booking_status_display(self, obj):
        """预订单状态显示名称"""
        status_map = {
            1: "草稿",
            2: "待媒体部初审",
            3: "待营运公司审核",
            4: "待媒体部复审",
            5: "已通过",
            6: "已完成",
            7: "已驳回",
            8: "已取消",
        }
        return status_map.get(obj.booking_status, "未知")

    def get_current_approval_node_display(self, obj):
        """当前审批节点显示名称"""
        node_map = {
            1: "媒体部初审",
            2: "营运公司审核",
            3: "媒体部复审",
        }
        return node_map.get(obj.current_approval_node, None)

    def validate_booking_no(self, value):
        """验证预订单号"""
        if not value or not value.strip():
            raise serializers.ValidationError("预订单号不能为空")
        return value.strip()

    def validate_booking_type(self, value):
        """验证预订单类型"""
        if value not in [1, 2, 3, 4]:
            raise serializers.ValidationError("预订单类型只能是：1=新预订, 2=续期, 3=变更, 4=重新发起")
        return value

    def validate_booking_status(self, value):
        """验证预订单状态"""
        if value not in [1, 2, 3, 4, 5, 6, 7, 8]:
            raise serializers.ValidationError("预订单状态只能是：1=草稿, 2=待媒体部初审, 3=待营运公司审核, 4=待媒体部复审, 5=已通过, 6=已完成, 7=已驳回, 8=已取消")
        return value

    def validate_paid_amount(self, value):
        """验证已支付金额"""
        if value is not None and value < 0:
            raise serializers.ValidationError("已支付金额不能为负数")
        return value

    def validate(self, attrs):
        """整体验证"""
        # 验证变更/续期订单必须有原预订单ID
        booking_type = attrs.get("booking_type")
        original_booking_id = attrs.get("original_booking_id")
        
        if booking_type in [2, 3, 4] and not original_booking_id:
            raise serializers.ValidationError("变更或续期预订单必须关联原预订单")

        # 验证已支付金额不能大于订单金额（如果两者都存在）
        total_amount = attrs.get("total_amount")
        paid_amount = attrs.get("paid_amount")
        
        if total_amount is not None and paid_amount is not None and paid_amount > total_amount:
            raise serializers.ValidationError("已支付金额不能大于订单金额")

        return attrs


class BookingOrderModelCreateSerializer(BookingOrderModelSerializer):
    """
    预订订单创建序列化器

    功能说明:
    - 专门用于创建新预订订单时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(BookingOrderModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            **BookingOrderModelSerializer.Meta.extra_kwargs,
            "booking_no": {"required": True, "allow_null": False, "allow_blank": False},
            "customer_id": {"required": True, "allow_null": False},
            "booking_type": {"required": True, "allow_null": False},
            "booking_status": {"required": True, "allow_null": False},
        }

    def create(self, validated_data):
        """创建预订订单时自动生成预订单号（如果未提供）"""
        booking_no = validated_data.get('booking_no')
        if not booking_no:
            # 自动生成预订单号：BK-YYYYMMDD-XXXX
            from datetime import datetime
            import random
            date_str = datetime.now().strftime('%Y%m%d')
            random_str = str(random.randint(1000, 9999))
            validated_data['booking_no'] = f"BK-{date_str}-{random_str}"
        
        # 自动填充客户名称（如果未提供）
        customer_id = validated_data.get('customer_id')
        if customer_id and not validated_data.get('customer_name'):
            try:
                customer = customer_id
                if hasattr(customer, 'company_name'):
                    validated_data['customer_name'] = customer.company_name
            except:
                pass
        
        return super().create(validated_data)


class BookingOrderModelUpdateSerializer(BookingOrderModelSerializer):
    """
    预订订单更新序列化器

    功能说明:
    - 专门用于更新现有预订订单时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(BookingOrderModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime", "booking_no"]

    def update(self, instance, validated_data):
        """更新时自动更新客户名称"""
        # 自动更新客户名称（如果客户ID变化）
        customer_id = validated_data.get('customer_id')
        if customer_id and customer_id != instance.customer_id:
            try:
                if hasattr(customer_id, 'company_name'):
                    validated_data['customer_name'] = customer_id.company_name
            except:
                pass
        
        return super().update(instance, validated_data)


class BookingOrderModelListSerializer(BookingOrderModelSerializer):
    """
    预订订单列表序列化器

    功能说明:
    - 专门用于预订订单列表显示,优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量,提高响应速度
    - 所有字段为只读,确保数据安全
    """

    class Meta:
        model = BookingOrderModel
        fields = [
            # 基础信息字段
            "id",
            "booking_no",
            "customer_id",
            "customer_name",

            # 订单类型和状态
            "booking_type",
            "booking_type_display",
            "original_booking_id",
            "booking_status",
            "booking_status_display",

            # 审批节点
            "current_approval_node",
            "current_approval_node_display",

            # 广告内容
            "ad_content",

            # 投放时间
            "start_date",
            "end_date",
            "duration_days",

            # 金额信息
            "total_amount",
            "paid_amount",

            # 审批和提交信息
            "approved_time",
            "submitter_id",
            "submit_time",

            # 驳回信息
            "reject_reason",
            "reject_node",
            "reject_user_id",
            "reject_time",

            # 备注
            "remark",

            # 计算显示字段
            "is_enabled",

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

