"""
Description: 客户序列化器
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import CustomerModel


class CustomerModelSerializer(CustomModelSerializer):
    """
    客户序列化器

    功能说明:
    - 提供客户数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer,获得审计字段自动填充功能
    """

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()

    # 计算字段 - 行业分类显示名称
    industry_display = serializers.SerializerMethodField()

    # 计算字段 - 客户等级显示名称
    customer_level_display = serializers.SerializerMethodField()

    # 计算字段 - 状态显示名称
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = CustomerModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "agent_id": {"required": False, "allow_null": True},
            "customer_code": {"required": True, "allow_null": False, "allow_blank": False},
            "company_name": {"required": True, "allow_null": False, "allow_blank": False},
            "credit_code": {"required": False, "allow_null": True, "allow_blank": True},
            "industry": {"required": False, "allow_null": True},
            "industry_tags": {"required": False, "allow_null": True, "allow_blank": True},
            "contact_name": {"required": False, "allow_null": True, "allow_blank": True},
            "contact_phone": {"required": False, "allow_null": True, "allow_blank": True},
            "contact_email": {"required": False, "allow_null": True, "allow_blank": True},
            "company_address": {"required": False, "allow_null": True, "allow_blank": True},
            "customer_level": {"required": False, "allow_null": True},
            "first_cooperation_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "last_cooperation_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "total_amount": {"required": False, "allow_null": True, "max_digits": 15, "decimal_places": 2},
            "cooperation_count": {"required": False, "allow_null": True},
            "status": {"required": True, "allow_null": False},
            "remark": {"required": False, "allow_null": True, "allow_blank": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0

    def get_industry_display(self, obj):
        """行业分类显示名称"""
        if obj.industry is None:
            return None
        industry_map = {
            1: "快消",
            2: "金融",
            3: "地产",
            4: "互联网",
            5: "其他",
        }
        return industry_map.get(obj.industry, "未知")

    def get_customer_level_display(self, obj):
        """客户等级显示名称"""
        if obj.customer_level is None:
            return None
        level_map = {
            1: "重点客户",
            2: "普通客户",
            3: "潜在客户",
        }
        return level_map.get(obj.customer_level, "未知")

    def get_status_display(self, obj):
        """状态显示名称"""
        status_map = {
            1: "活跃",
            2: "休眠",
            3: "流失",
        }
        return status_map.get(obj.status, "未知")

    def validate_customer_code(self, value):
        """验证客户编码"""
        if not value or not value.strip():
            raise serializers.ValidationError("客户编码不能为空")
        return value.strip()

    def validate_company_name(self, value):
        """验证公司名称"""
        if not value or not value.strip():
            raise serializers.ValidationError("公司名称不能为空")
        return value.strip()

    def validate_industry(self, value):
        """验证行业分类"""
        if value is not None and value not in [1, 2, 3, 4, 5]:
            raise serializers.ValidationError("行业分类只能是：1=快消, 2=金融, 3=地产, 4=互联网, 5=其他")
        return value

    def validate_customer_level(self, value):
        """验证客户等级"""
        if value is not None and value not in [1, 2, 3]:
            raise serializers.ValidationError("客户等级只能是：1=重点客户, 2=普通客户, 3=潜在客户")
        return value

    def validate_status(self, value):
        """验证状态"""
        if value not in [1, 2, 3]:
            raise serializers.ValidationError("状态只能是：1=活跃, 2=休眠, 3=流失")
        return value

    def validate_total_amount(self, value):
        """验证累计合作金额"""
        if value is not None and value < 0:
            raise serializers.ValidationError("累计合作金额不能为负数")
        return value

    def validate_cooperation_count(self, value):
        """验证累计合作次数"""
        if value is not None and value < 0:
            raise serializers.ValidationError("累计合作次数不能为负数")
        return value

    def validate_contact_email(self, value):
        """验证联系邮箱"""
        if value:
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, value):
                raise serializers.ValidationError("邮箱格式不正确")
        return value

    def validate(self, attrs):
        """整体验证"""
        # 验证合作日期
        first_cooperation_date = attrs.get("first_cooperation_date")
        last_cooperation_date = attrs.get("last_cooperation_date")

        if first_cooperation_date and last_cooperation_date and first_cooperation_date > last_cooperation_date:
            raise serializers.ValidationError("首次合作时间不能晚于最近合作时间")

        return attrs


class CustomerModelCreateSerializer(CustomerModelSerializer):
    """
    客户创建序列化器

    功能说明:
    - 专门用于创建新客户时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(CustomerModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            **CustomerModelSerializer.Meta.extra_kwargs,
            "customer_code": {"required": True, "allow_null": False, "allow_blank": False},
            "company_name": {"required": True, "allow_null": False, "allow_blank": False},
            "status": {"required": True, "allow_null": False},
        }

    def create(self, validated_data):
        """创建客户时自动生成客户编码（如果未提供）"""
        customer_code = validated_data.get('customer_code')
        if not customer_code:
            # 自动生成客户编码：CU-YYYYMMDD-XXXX
            from datetime import datetime
            import random
            date_str = datetime.now().strftime('%Y%m%d')
            random_str = str(random.randint(1000, 9999))
            validated_data['customer_code'] = f"CU-{date_str}-{random_str}"
        return super().create(validated_data)


class CustomerModelUpdateSerializer(CustomerModelSerializer):
    """
    客户更新序列化器

    功能说明:
    - 专门用于更新现有客户时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(CustomerModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime", "customer_code"]


class CustomerModelListSerializer(CustomerModelSerializer):
    """
    客户列表序列化器

    功能说明:
    - 专门用于客户列表显示,优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量,提高响应速度
    - 所有字段为只读,确保数据安全
    """

    class Meta:
        model = CustomerModel
        fields = [
            # 基础信息字段
            "id",
            "customer_code",
            "company_name",
            "credit_code",
            
            # 归属信息
            "agent_id",
            
            # 行业信息
            "industry",
            "industry_display",
            "industry_tags",
            
            # 联系信息
            "contact_name",
            "contact_phone",
            "contact_email",
            "company_address",
            
            # 客户信息
            "customer_level",
            "customer_level_display",
            "status",
            "status_display",
            
            # 合作信息
            "first_cooperation_date",
            "last_cooperation_date",
            "total_amount",
            "cooperation_count",
            
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

