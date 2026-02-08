"""
Description: 公司模型序列化器
Version: 1.0
Autor: 王晨
Date: 2025-10-10 09:50:00
LastEditors: 王晨
LastEditTime: 2025-10-10 10:58:38
"""

import uuid
from rest_framework import serializers
from django.utils import timezone
from dvadmin.utils.serializers import CustomModelSerializer
from dvadmin.utils.string_util import get_date_object
from .models import CompanyModel


class CompanyModelSerializer(CustomModelSerializer):
    """
    公司模型序列化器

    功能说明：
    - 提供公司数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 自动计算显示字段（如状态等）
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer，获得审计字段自动填充功能
    """

    # 计算字段 - 公司状态
    company_status = serializers.SerializerMethodField()

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()

    # 小写字段别名（序列化/反序列化映射）
    encode = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    shortname = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    fullname = serializers.CharField(required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = CompanyModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            # 数字字段类型配置
            "category": {"required": True, "allow_null": False},
            "parentid": {"required": False, "allow_null": True},
            "sortcode": {
                "required": True,
                "allow_null": False,
                "error_messages": {"required": "该字段是必填项。"},
            },
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
            # 字符串字段类型配置（统一小写入口）
            "encode": {"required": False, "allow_null": True, "allow_blank": True},
            "shortname": {"required": False, "allow_null": True, "allow_blank": True},
            "fullname": {"required": False, "allow_null": True, "allow_blank": True},
            "nature": {"required": False, "allow_null": True, "allow_blank": True},
            "outerPhone": {"required": False, "allow_null": True, "allow_blank": True},
            "innerPhone": {"required": False, "allow_null": True, "allow_blank": True},
            "fax": {"required": False, "allow_null": True, "allow_blank": True},
            "postalcode": {"required": False, "allow_null": True, "allow_blank": True},
            "email": {"required": False, "allow_null": True, "allow_blank": True},
            "manager": {"required": False, "allow_null": True, "allow_blank": True},
            "provinceId": {"required": False, "allow_null": True, "allow_blank": True},
            "cityId": {"required": False, "allow_null": True, "allow_blank": True},
            "countyId": {"required": False, "allow_null": True, "allow_blank": True},
            "address": {"required": False, "allow_null": True, "allow_blank": True},
            "webAddress": {"required": False, "allow_null": True, "allow_blank": True},
            "businessScope": {"required": False, "allow_null": True, "allow_blank": True},
            # 日期字段类型配置
            "foundedTime": {"required": False, "allow_null": True, "format": "%Y-%m-%d %H:%M:%S", "input_formats": ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]},
        }

    def get_company_status(self, obj):
        """计算公司状态"""
        if obj.enabled_mark == 0:
            return "已禁用"
        elif obj.delete_mark == 1:
            return "已删除"
        else:
            return "正常"

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0

    def validate_fullname(self, value):
        """验证公司全称"""
        if value and isinstance(value, str):
            return value.strip()
        return value

    def validate_shortname(self, value):
        """验证公司简称"""
        if value and isinstance(value, str):
            return value.strip()
        return value

    def validate_email(self, value):
        """验证邮箱格式"""
        if value and isinstance(value, str):
            value = value.strip()
            if value and '@' not in value:
                raise serializers.ValidationError("邮箱格式不正确")
        return value

    def validate_sortcode(self, value):
        """验证排序码"""
        if value is None:
            raise serializers.ValidationError("排序码不能为空")
        if value < 0:
            raise serializers.ValidationError("排序码不能为负数")
        return value

    def validate_category(self, value):
        """验证公司分类"""
        if value is None:
            raise serializers.ValidationError("公司分类不能为空")
        return value

    def validate(self, attrs):
        """整体验证"""
        # 验证parentid如果存在
        parent_id = attrs.get("parentid")
        if parent_id is not None:
            # 如果当前对象存在，不能将自己的ID设为parentid
            if self.instance and self.instance.id == parent_id:
                raise serializers.ValidationError("不能将自己设置为上级公司")
        
        return attrs


class CompanyModelCreateSerializer(CompanyModelSerializer):
    """
    公司创建序列化器

    功能说明：
    - 专门用于创建新公司时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(CompanyModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            **CompanyModelSerializer.Meta.extra_kwargs,
            "fullname": {"required": True},
            "category": {"required": True, "allow_null": False},
            "sortcode": {"required": True, "allow_null": False},
        }

    def create(self, validated_data):
        """创建公司"""
        # 调用父类的create方法
        return super().create(validated_data)

    def to_internal_value(self, data):
        # 接受小写字段并映射到模型字段
        data = data.copy()
        # encode / fullname 已与模型字段一致
        if 'shortname' in data:
            # shortname 已经是模型字段名，不需要映射
            pass
        # fullname 已经是模型字段名
        return super().to_internal_value(data)


class CompanyModelUpdateSerializer(CompanyModelSerializer):
    """
    公司更新序列化器

    功能说明：
    - 专门用于更新现有公司时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID及早建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(CompanyModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime"]

    def to_internal_value(self, data):
        data = data.copy()
        # encode 已与模型字段一致
        if 'shortname' in data:
            # shortname 已经是模型字段名，不需要映射
            pass
        # fullname 已与模型字段一致
        return super().to_internal_value(data)


class CompanyModelListSerializer(CompanyModelSerializer):
    """
    公司列表序列化器

    功能说明：
    - 专门用于公司列表显示，优化性能
    - 只包含列表展示需要的核心字段
    - 包含计算字段（状态等）
    - 减少数据传输量，提高响应速度
    - 所有字段为只读，确保数据安全
    """

    # 树表支持字段
    hasChild = serializers.SerializerMethodField()
    pcode_info = serializers.SerializerMethodField()

    def get_hasChild(self, obj):
        """是否有子节点（用于树懒加载）"""
        return CompanyModel.objects.filter(parentid=obj.id, delete_mark=0, enabled_mark=1).exists()

    def get_pcode_info(self, obj):
        """上级公司显示信息（用于选择器回显）"""
        if not obj.parentid:
            return None
        parent = CompanyModel.objects.filter(id=obj.parentid).values("shortname", "id").first()
        if not parent:
            return None
        return parent.get("shortname") or ""

    # 小写字段输出
    encode = serializers.CharField(read_only=True)
    shortname = serializers.CharField(read_only=True)
    fullname = serializers.CharField(read_only=True)

    class Meta:
        model = CompanyModel
        fields = [
            # 基础信息字段
            "id",
            "encode",
            "shortname",
            "fullname",
            "category",
            "parentid",
            
            # 联系方式字段
            "outerPhone",
            "innerPhone",
            "email",
            "manager",
            
            # 地址字段
            "provinceId",
            "cityId",
            "countyId",
            "address",
            
            # 其他信息字段
            "nature",
            "fax",
            "postalcode",
            "webAddress",
            "foundedTime",
            "businessScope",
            "sortcode",
            
            # 状态字段
            "enabled_mark",
            "delete_mark",
            
            # 计算显示字段
            "company_status",
            "is_enabled",
            "hasChild",
            "pcode_info",
            
            # 审计字段
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
        ]
        read_only_fields = fields


class CompanyModelImportSerializer(CustomModelSerializer):
    """
    公司导入序列化器
    
    功能说明：
    - 专门用于Excel导入功能
    - 包含导入字段：公司名称、编码、分类等
    - 每次导入都会创建新的公司记录
    - 除必填字段外，其他字段均允许为空
    """
    
    class Meta:
        model = CompanyModel
        fields = [
            'fullName',          # 公司全称
            'shortname',         # 公司简称
            'enCode',            # 编码（导入支持原模型字段）
            'category',          # 公司分类
            'sortcode',          # 排序码
            'nature',            # 公司性质
            'outerPhone',        # 外线电话
            'email',             # 邮箱
            'manager',           # 负责人
            'address',           # 详细地址
            'enabled_mark',      # 公司状态
        ]
        extra_kwargs = {
            'fullName': {'required': True},  # 公司全称必填
            'category': {'required': True},  # 公司分类必填
            'sortcode': {'required': True},  # 排序码必填
            'shortname': {'required': False, 'allow_null': True, 'allow_blank': True},
            'enCode': {'required': False, 'allow_null': True, 'allow_blank': True},
            'nature': {'required': False, 'allow_null': True, 'allow_blank': True},
            'outerPhone': {'required': False, 'allow_null': True, 'allow_blank': True},
            'email': {'required': False, 'allow_null': True, 'allow_blank': True},
            'manager': {'required': False, 'allow_null': True, 'allow_blank': True},
            'address': {'required': False, 'allow_null': True, 'allow_blank': True},
            'enabled_mark': {'required': False, 'allow_null': True},
        }
    
    def validate_fullName(self, value):
        """验证公司全称（必填）"""
        if not value or not value.strip():
            raise serializers.ValidationError("公司全称不能为空")
        return value.strip()
    
    def validate_category(self, value):
        """验证公司分类（必填）"""
        if value is None:
            raise serializers.ValidationError("公司分类不能为空")
        return value
    
    def validate_sortCode(self, value):
        """验证排序码（必填）"""
        if value is None:
            raise serializers.ValidationError("排序码不能为空")
        if value < 0:
            raise serializers.ValidationError("排序码不能为负数")
        return value
    
    def validate_email(self, value):
        """验证邮箱格式"""
        if value and isinstance(value, str):
            value = value.strip()
            if value and '@' not in value:
                raise serializers.ValidationError("邮箱格式不正确")
        return value
    
    def validate_enabled_mark(self, value):
        """验证公司状态"""
        if value is not None and value not in [0, 1]:
            raise serializers.ValidationError("公司状态只能是0(禁用)或1(启用)")
        return value
    
    def create(self, validated_data):
        """创建新公司"""
        # 如果没有指定公司状态，默认为启用
        if 'enabled_mark' not in validated_data:
            validated_data['enabled_mark'] = 1
        
        # 如果没有指定delete_mark，默认为0（未删除）
        if 'delete_mark' not in validated_data:
            validated_data['delete_mark'] = 0
        
        return CompanyModel.objects.create(**validated_data)

