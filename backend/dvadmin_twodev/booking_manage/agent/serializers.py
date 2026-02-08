"""
Description: 代理商序列化器
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import AgentModel


class AgentModelSerializer(CustomModelSerializer):
    """
    代理商序列化器

    功能说明:
    - 提供代理商数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer,获得审计字段自动填充功能
    """

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()

    # 计算字段 - 合作等级显示名称
    cooperation_level_display = serializers.SerializerMethodField()

    # 计算字段 - 结算方式显示名称
    settlement_type_display = serializers.SerializerMethodField()

    class Meta:
        model = AgentModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "agent_code": {"required": True, "allow_null": False, "allow_blank": False},
            "company_name": {"required": True, "allow_null": False, "allow_blank": False},
            "credit_code": {"required": False, "allow_null": True, "allow_blank": True},
            "legal_person": {"required": False, "allow_null": True, "allow_blank": True},
            "registered_capital": {"required": False, "allow_null": True, "max_digits": 15, "decimal_places": 2},
            "established_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "company_address": {"required": False, "allow_null": True, "allow_blank": True},
            "contact_phone": {"required": False, "allow_null": True, "allow_blank": True},
            "contact_email": {"required": False, "allow_null": True, "allow_blank": True},
            "cooperation_level": {"required": True, "allow_null": False},
            "contract_start_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "contract_end_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "settlement_type": {"required": False, "allow_null": True},
            "bank_name": {"required": False, "allow_null": True, "allow_blank": True},
            "bank_account": {"required": False, "allow_null": True, "allow_blank": True},
            "business_manager": {"required": False, "allow_null": True, "allow_blank": True},
            "remark": {"required": False, "allow_null": True, "allow_blank": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0

    def get_cooperation_level_display(self, obj):
        """合作等级显示名称"""
        level_map = {
            1: "A级",
            2: "B级",
            3: "C级",
        }
        return level_map.get(obj.cooperation_level, "未知")

    def get_settlement_type_display(self, obj):
        """结算方式显示名称"""
        if obj.settlement_type is None:
            return None
        type_map = {
            1: "月结",
            2: "季结",
            3: "年结",
        }
        return type_map.get(obj.settlement_type, "未知")

    def validate_agent_code(self, value):
        """验证代理商编码"""
        if not value or not value.strip():
            raise serializers.ValidationError("代理商编码不能为空")
        return value.strip()

    def validate_company_name(self, value):
        """验证公司名称"""
        if not value or not value.strip():
            raise serializers.ValidationError("公司名称不能为空")
        return value.strip()

    def validate_cooperation_level(self, value):
        """验证合作等级"""
        if value not in [1, 2, 3]:
            raise serializers.ValidationError("合作等级只能是：1=A级, 2=B级, 3=C级")
        return value

    def validate_settlement_type(self, value):
        """验证结算方式"""
        if value is not None and value not in [1, 2, 3]:
            raise serializers.ValidationError("结算方式只能是：1=月结, 2=季结, 3=年结")
        return value

    def validate_registered_capital(self, value):
        """验证注册资本"""
        if value is not None and value < 0:
            raise serializers.ValidationError("注册资本不能为负数")
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
        # 验证合同日期
        contract_start_date = attrs.get("contract_start_date")
        contract_end_date = attrs.get("contract_end_date")

        if contract_start_date and contract_end_date and contract_start_date > contract_end_date:
            raise serializers.ValidationError("合同开始日期不能晚于合同结束日期")

        # 验证成立日期和合同日期
        established_date = attrs.get("established_date")
        if established_date and contract_start_date and established_date > contract_start_date:
            raise serializers.ValidationError("成立日期不能晚于合同开始日期")

        return attrs


class AgentModelCreateSerializer(AgentModelSerializer):
    """
    代理商创建序列化器

    功能说明:
    - 专门用于创建新代理商时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(AgentModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            **AgentModelSerializer.Meta.extra_kwargs,
            "agent_code": {"required": True, "allow_null": False, "allow_blank": False},
            "company_name": {"required": True, "allow_null": False, "allow_blank": False},
            "cooperation_level": {"required": True, "allow_null": False},
        }

    def create(self, validated_data):
        """创建代理商时自动生成代理商编码（如果未提供）"""
        agent_code = validated_data.get('agent_code')
        if not agent_code:
            # 自动生成代理商编码：AG-YYYYMMDD-XXXX
            from datetime import datetime
            import random
            date_str = datetime.now().strftime('%Y%m%d')
            random_str = str(random.randint(1000, 9999))
            validated_data['agent_code'] = f"AG-{date_str}-{random_str}"
        return super().create(validated_data)


class AgentModelUpdateSerializer(AgentModelSerializer):
    """
    代理商更新序列化器

    功能说明:
    - 专门用于更新现有代理商时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(AgentModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime", "agent_code"]


class AgentModelListSerializer(AgentModelSerializer):
    """
    代理商列表序列化器

    功能说明:
    - 专门用于代理商列表显示,优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量,提高响应速度
    - 所有字段为只读,确保数据安全
    """

    class Meta:
        model = AgentModel
        fields = [
            # 基础信息字段
            "id",
            "agent_code",
            "company_name",
            "credit_code",
            "legal_person",
            
            # 公司信息
            "registered_capital",
            "established_date",
            "company_address",
            
            # 联系信息
            "contact_phone",
            "contact_email",
            
            # 合作信息
            "cooperation_level",
            "cooperation_level_display",
            "contract_start_date",
            "contract_end_date",
            
            # 结算信息
            "settlement_type",
            "settlement_type_display",
            "bank_name",
            "bank_account",
            
            # 业务信息
            "business_manager",
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

