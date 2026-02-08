"""
Description: 预订订单明细序列化器
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import BookingOrderDetailModel


class BookingOrderDetailModelSerializer(CustomModelSerializer):
    """
    预订订单明细序列化器

    功能说明:
    - 提供预订订单明细数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer,获得审计字段自动填充功能
    """

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()

    # 计算字段 - 资源锁定状态显示名称
    lock_status_display = serializers.SerializerMethodField()

    class Meta:
        model = BookingOrderDetailModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "booking_order_id": {"required": True, "allow_null": False},
            "roadline_id": {"required": True, "allow_null": False},
            "roadline_name": {"required": False, "allow_null": True, "allow_blank": True},
            "roadline_company_id": {"required": True, "allow_null": False},
            "roadline_company_name": {"required": False, "allow_null": True, "allow_blank": True},
            "media_type_id": {"required": True, "allow_null": False},
            "media_type_name": {"required": False, "allow_null": True, "allow_blank": True},
            "is_composite": {"required": False, "allow_null": True},
            "quantity": {"required": True, "allow_null": False},
            "unit_price": {"required": False, "allow_null": True, "max_digits": 10, "decimal_places": 2},
            "subtotal_amount": {"required": False, "allow_null": True, "max_digits": 15, "decimal_places": 2},
            "lock_status": {"required": False, "allow_null": True},
            "start_date": {"required": True, "allow_null": False},
            "end_date": {"required": True, "allow_null": False},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0

    def get_lock_status_display(self, obj):
        """资源锁定状态显示名称"""
        status_map = {
            1: "未锁定",
            2: "已锁定",
            3: "已释放",
        }
        return status_map.get(obj.lock_status, "未知")

    def validate_quantity(self, value):
        """验证预订数量"""
        if value is None or value <= 0:
            raise serializers.ValidationError("预订数量必须大于0")
        return value

    def validate(self, attrs):
        """整体验证"""
        return attrs


class BookingOrderDetailModelCreateSerializer(BookingOrderDetailModelSerializer):
    """
    预订订单明细创建序列化器

    功能说明:
    - 专门用于创建新预订订单明细时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(BookingOrderDetailModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            **BookingOrderDetailModelSerializer.Meta.extra_kwargs,
            "booking_order_id": {"required": True, "allow_null": False},
            "roadline_id": {"required": True, "allow_null": False},
            "roadline_company_id": {"required": True, "allow_null": False},
            "media_type_id": {"required": True, "allow_null": False},
            "quantity": {"required": True, "allow_null": False},
        }

    def create(self, validated_data):
        """创建预订订单明细时自动填充冗余字段"""
        # 自动填充线路名称
        roadline_id = validated_data.get('roadline_id')
        if roadline_id and not validated_data.get('roadline_name'):
            try:
                if hasattr(roadline_id, 'line_name'):
                    validated_data['roadline_name'] = roadline_id.line_name
            except:
                pass

        # 自动填充营运公司名称
        roadline_company_id = validated_data.get('roadline_company_id')
        if roadline_company_id and not validated_data.get('roadline_company_name'):
            try:
                if hasattr(roadline_company_id, 'company_name'):
                    validated_data['roadline_company_name'] = roadline_company_id.company_name
            except:
                pass

        # 自动填充媒体类型名称和is_composite字段
        media_type_id = validated_data.get('media_type_id')
        if media_type_id:
            try:
                if hasattr(media_type_id, 'media_name') and not validated_data.get('media_type_name'):
                    validated_data['media_type_name'] = media_type_id.media_name
                # 自动从媒体类型获取is_composite字段
                if hasattr(media_type_id, 'is_composite'):
                    validated_data['is_composite'] = media_type_id.is_composite
            except Exception as e:
                print(f"[明细创建] 获取媒体类型信息失败: {e}")
                pass

        return super().create(validated_data)


class BookingOrderDetailModelUpdateSerializer(BookingOrderDetailModelSerializer):
    """
    预订订单明细更新序列化器

    功能说明:
    - 专门用于更新现有预订订单明细时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(BookingOrderDetailModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime", "booking_order_id"]

    def update(self, instance, validated_data):
        """更新时自动填充冗余字段"""
        # 自动更新线路名称（如果线路ID变化）
        roadline_id = validated_data.get('roadline_id')
        if roadline_id and roadline_id != instance.roadline_id:
            try:
                if hasattr(roadline_id, 'line_name'):
                    validated_data['roadline_name'] = roadline_id.line_name
            except:
                pass

        # 自动更新营运公司名称（如果营运公司ID变化）
        roadline_company_id = validated_data.get('roadline_company_id')
        if roadline_company_id and roadline_company_id != instance.roadline_company_id:
            try:
                if hasattr(roadline_company_id, 'company_name'):
                    validated_data['roadline_company_name'] = roadline_company_id.company_name
            except:
                pass

        # 自动更新媒体类型名称和is_composite字段（如果媒体类型ID变化）
        media_type_id = validated_data.get('media_type_id')
        if media_type_id and media_type_id != instance.media_type_id:
            try:
                if hasattr(media_type_id, 'media_name'):
                    validated_data['media_type_name'] = media_type_id.media_name
                # 自动从媒体类型获取is_composite字段
                if hasattr(media_type_id, 'is_composite'):
                    validated_data['is_composite'] = media_type_id.is_composite
            except Exception as e:
                print(f"[明细更新] 获取媒体类型信息失败: {e}")
                pass

        return super().update(instance, validated_data)


class BookingOrderDetailModelListSerializer(BookingOrderDetailModelSerializer):
    """
    预订订单明细列表序列化器

    功能说明:
    - 专门用于预订订单明细列表显示,优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量,提高响应速度
    - 所有字段为只读,确保数据安全
    """

    class Meta:
        model = BookingOrderDetailModel
        fields = [
            # 基础信息字段
            "id",
            "booking_order_id",
            
            # 线路信息
            "roadline_id",
            "roadline_name",
            "roadline_company_id",
            "roadline_company_name",
            
            # 媒体类型信息
            "media_type_id",
            "media_type_name",
            "is_composite",
            
            # 预订信息
            "quantity",
            "unit_price",
            "subtotal_amount",
            "start_date",
            "end_date",
            
            # 锁定状态
            "lock_status",
            "lock_status_display",
            
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

