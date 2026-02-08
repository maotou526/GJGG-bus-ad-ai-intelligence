"""
Description: 媒体类型模型序列化器
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import AdMediaTypeModel


class AdMediaTypeModelSerializer(CustomModelSerializer):
    """
    媒体类型模型序列化器

    功能说明：
    - 提供媒体类型数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 自动计算显示字段（如类别名称等）
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer，获得审计字段自动填充功能
    """

    # 计算字段 - 大类归属显示名称
    media_category_display = serializers.SerializerMethodField()

    # 计算字段 - 是否组合类型显示名称
    is_composite_display = serializers.SerializerMethodField()

    class Meta:
        model = AdMediaTypeModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "media_name": {"required": True, "allow_null": False, "allow_blank": False},
            "media_category": {"required": True, "allow_null": False},
            "is_composite": {"required": True, "allow_null": False},
            "spec_config": {"required": False, "allow_null": True},
            "fabrication_req": {"required": False, "allow_null": True, "allow_blank": True},
            "base_price": {"required": False, "allow_null": True},
            "sort_order": {"required": False, "allow_null": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_media_category_display(self, obj):
        """大类归属显示名称"""
        category_map = {
            1: "车身广告",
            2: "站点广告",
        }
        return category_map.get(obj.media_category, "未知")

    def get_is_composite_display(self, obj):
        """是否组合类型显示名称"""
        return "组合类型" if obj.is_composite else "基础类型"

    def validate_media_name(self, value):
        """验证类型名称"""
        if not value or not value.strip():
            raise serializers.ValidationError("类型名称不能为空")
        return value.strip()

    def validate_media_category(self, value):
        """验证大类归属"""
        if value not in [1, 2]:
            raise serializers.ValidationError("大类归属只能是：1=车身广告, 2=站点广告")
        return value

    def validate_base_price(self, value):
        """验证刊例价基准"""
        if value is not None and value < 0:
            raise serializers.ValidationError("刊例价基准不能为负数")
        return value

    def validate_sort_order(self, value):
        """验证显示顺序"""
        if value is not None and value < 0:
            raise serializers.ValidationError("显示顺序不能为负数")
        return value

    def validate(self, attrs):
        """整体验证"""
        return attrs


class AdMediaTypeModelCreateSerializer(AdMediaTypeModelSerializer):
    """
    媒体类型创建序列化器

    功能说明：
    - 专门用于创建新媒体类型时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(AdMediaTypeModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            "media_name": {"required": True},
            "media_category": {"required": True},
            "is_composite": {"required": True},
            "spec_config": {"required": False, "allow_null": True},
            "fabrication_req": {"required": False, "allow_null": True, "allow_blank": True},
            "base_price": {"required": False, "allow_null": True},
            "sort_order": {"required": False, "allow_null": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def validate(self, attrs):
        """创建时的验证，检查类型名称是否重复"""
        attrs = super().validate(attrs)
        
        media_name = attrs.get('media_name')
        if media_name:
            # 检查是否存在相同名称的媒体类型（排除已删除的）
            existing = AdMediaTypeModel.objects.filter(
                media_name=media_name,
                delete_mark=0
            ).first()
            
            if existing:
                raise serializers.ValidationError({
                    'media_name': f'类型名称"{media_name}"已存在，不能重复'
                })
        
        return attrs

    def create(self, validated_data):
        """创建媒体类型"""
        # 调用父类的create方法
        return super().create(validated_data)


class AdMediaTypeModelUpdateSerializer(AdMediaTypeModelSerializer):
    """
    媒体类型更新序列化器

    功能说明：
    - 专门用于更新现有媒体类型时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(AdMediaTypeModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime"]

    def validate(self, attrs):
        """更新时的验证，检查类型名称是否重复"""
        # 调用父类验证
        attrs = super().validate(attrs)
        
        media_name = attrs.get('media_name')
        if media_name and self.instance:
            # 如果类型名称有变化，检查是否存在相同名称的媒体类型（排除已删除的和当前记录）
            if media_name != self.instance.media_name:
                existing = AdMediaTypeModel.objects.filter(
                    media_name=media_name,
                    delete_mark=0
                ).exclude(id=self.instance.id).first()
                
                if existing:
                    raise serializers.ValidationError({
                        'media_name': f'类型名称"{media_name}"已存在，不能重复'
                    })
        
        return attrs


class AdMediaTypeModelListSerializer(AdMediaTypeModelSerializer):
    """
    媒体类型列表序列化器

    功能说明：
    - 专门用于媒体类型列表显示，优化性能
    - 只包含列表展示需要的核心字段
    - 包含计算字段（类别显示名称等）
    - 减少数据传输量，提高响应速度
    - 所有字段为只读，确保数据安全
    """

    class Meta:
        model = AdMediaTypeModel
        fields = [
            # 基础信息字段
            "id",
            "media_name",
            "media_category",
            "is_composite",
            "spec_config",
            "fabrication_req",
            "base_price",
            "sort_order",
            
            # 计算显示字段
            "media_category_display",
            "is_composite_display",
            
            # 状态字段
            "enabled_mark",
            "delete_mark",
            
            # 审计字段
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
        ]
        read_only_fields = fields

