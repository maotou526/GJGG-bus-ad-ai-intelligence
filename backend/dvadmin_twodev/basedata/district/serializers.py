"""
Description: 区属模型序列化器
Version: 1.0
Autor: AI Assistant
Date: 2025-10-16
LastEditors: 
LastEditTime: 2025-10-16
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import DistrictModel


class DistrictModelSerializer(CustomModelSerializer):
    """
    区属模型序列化器

    功能说明：
    - 提供区属数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 自动计算显示字段（如类型名称等）
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer，获得审计字段自动填充功能
    """

    # 计算字段 - 区属类型显示名称
    type_display = serializers.SerializerMethodField()

    # 计算字段 - 父级区属名称
    parent_name = serializers.SerializerMethodField()

    # 计算字段 - 是否有子级
    has_children = serializers.SerializerMethodField()

    class Meta:
        model = DistrictModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "name": {"required": False, "allow_null": True, "allow_blank": True},
            "type": {"required": False, "allow_null": True, "allow_blank": True},
            "parent_id": {"required": False, "allow_null": True, "allow_blank": True},
            "fence": {"required": False, "allow_null": True, "allow_blank": True},
            "center_coord": {"required": False, "allow_null": True, "allow_blank": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_type_display(self, obj):
        """区属类型显示名称"""
        type_map = {
            "市": "市级",
            "区": "区级",
            "街道": "街道级",
        }
        return type_map.get(obj.type, obj.type) if obj.type else "未知"

    def get_parent_name(self, obj):
        """获取父级区属名称"""
        if obj.parent_id:
            try:
                parent = DistrictModel.objects.filter(id=obj.parent_id).first()
                return parent.name if parent else "未找到"
            except Exception:
                return "未找到"
        return None

    def get_has_children(self, obj):
        """是否有子级区属"""
        return DistrictModel.objects.filter(parent_id=obj.id).exists()

    def validate_name(self, value):
        """验证区属名称"""
        if not value or not value.strip():
            raise serializers.ValidationError("区属名称不能为空")
        return value.strip()

    def validate_type(self, value):
        """验证区属类型"""
        if value and value not in ["市", "区", "街道"]:
            raise serializers.ValidationError("区属类型只能是：市、区、街道")
        return value

    def validate_parent_id(self, value):
        """验证父级区属ID"""
        if value:
            # 检查父级区属是否存在
            if not DistrictModel.objects.filter(id=value, delete_mark=0).exists():
                raise serializers.ValidationError("父级区属不存在或已删除")
        return value

   
    
    def validate(self, attrs):
        """整体验证"""
        # 验证层级关系
        parent_id = attrs.get("parent_id")
        current_type = attrs.get("type")
        
        if parent_id and current_type:
            parent = DistrictModel.objects.filter(id=parent_id).first()
            if parent:
                # 验证层级类型逻辑
                type_hierarchy = {"市": 0, "区": 1, "街道": 2}
                parent_level = type_hierarchy.get(parent.type, -1)
                current_level = type_hierarchy.get(current_type, -1)
                
                if parent_level >= current_level:
                    raise serializers.ValidationError({
                        "type": f"类型层级错误：{parent.type} 下不能有 {current_type}"
                    })

        return attrs


class DistrictModelCreateSerializer(DistrictModelSerializer):
    """
    区属创建序列化器

    功能说明：
    - 专门用于创建新区属时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(DistrictModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            "name": {"required": True},
            "type": {"required": True},
        }

    def create(self, validated_data):
        """创建区属"""
        # 调用父类的create方法
        return super().create(validated_data)


class DistrictModelUpdateSerializer(DistrictModelSerializer):
    """
    区属更新序列化器

    功能说明：
    - 专门用于更新现有区属时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(DistrictModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime"]

    def validate(self, attrs):
        """更新时的验证"""
        # 调用父类验证
        attrs = super().validate(attrs)
        
        # 防止将自己设置为父级
        parent_id = attrs.get("parent_id")
        if parent_id and str(parent_id) == str(self.instance.id):
            raise serializers.ValidationError({
                "parent_id": "不能将自己设置为父级区属"
            })
        
        # 检查是否存在循环引用
        if parent_id:
            current_parent = parent_id
            visited = set([str(self.instance.id)])
            while current_parent:
                if str(current_parent) in visited:
                    raise serializers.ValidationError({
                        "parent_id": "不能形成循环引用"
                    })
                visited.add(str(current_parent))
                parent = DistrictModel.objects.filter(id=current_parent).first()
                current_parent = parent.parent_id if parent else None
        
        return attrs


class DistrictModelListSerializer(DistrictModelSerializer):
    """
    区属列表序列化器

    功能说明：
    - 专门用于区属列表显示，优化性能
    - 只包含列表展示需要的核心字段
    - 包含计算字段（类型显示名称等）
    - 减少数据传输量，提高响应速度
    - 所有字段为只读，确保数据安全
    """

    class Meta:
        model = DistrictModel
        fields = [
            # 基础信息字段
            "id",
            "name",
            "type",
            "parent_id",
            "center_coord",
            
            # 计算显示字段
            "type_display",
            "parent_name",
            "has_children",
            
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


class DistrictTreeSerializer(serializers.ModelSerializer):
    """
    区属树形结构序列化器

    功能说明：
    - 用于生成区属的树形结构数据
    - 支持递归获取子级数据
    - 适用于级联选择器、树形菜单等场景
    """
    
    children = serializers.SerializerMethodField()
    label = serializers.CharField(source='name', read_only=True)
    value = serializers.IntegerField(source='id', read_only=True)
    
    class Meta:
        model = DistrictModel
        fields = ['id', 'name', 'type', 'parent_id', 'value', 'label', 'children']
    
    def get_children(self, obj):
        """获取子级区属"""
        children = DistrictModel.objects.filter(
            parent_id=obj.id,
            delete_mark=0,
            enabled_mark=1
        ).order_by('name')
        
        if children.exists():
            return DistrictTreeSerializer(children, many=True).data
        return []

