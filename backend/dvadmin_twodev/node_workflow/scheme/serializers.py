'''
Description: 流程模板序列化器
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import WorkflowSchemeModel


class WorkflowSchemeModelSerializer(CustomModelSerializer):
    """
    流程模板序列化器
    用于详情、更新等场景
    """
    
    # 计算字段 - 模板类型显示
    type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowSchemeModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "scheme_info": {"required": False, "allow_null": True},
            "type": {"required": True},
            "content": {"required": False, "allow_null": True, "allow_blank": True},
        }
    
    def get_type_display(self, obj):
        """获取模板类型显示"""
        type_map = {
            1: "正式",
            2: "草稿",
        }
        return type_map.get(obj.type, "未知")
    
    def validate_type(self, value):
        """验证模板类型"""
        if value not in [1, 2]:
            raise serializers.ValidationError("模板类型只能是1(正式)或2(草稿)")
        return value
    
    def validate_content(self, value):
        """验证流程内容（JSON格式）"""
        if value:
            import json
            try:
                json.loads(value)
            except json.JSONDecodeError:
                raise serializers.ValidationError("流程内容必须是有效的JSON格式")
        return value


class WorkflowSchemeModelCreateSerializer(WorkflowSchemeModelSerializer):
    """
    创建序列化器
    用于创建新记录时的验证
    """
    
    class Meta(WorkflowSchemeModelSerializer.Meta):
        extra_kwargs = {
            **WorkflowSchemeModelSerializer.Meta.extra_kwargs,
            "scheme_info": {"required": True},
            "type": {"required": True},
        }


class WorkflowSchemeModelUpdateSerializer(WorkflowSchemeModelSerializer):
    """
    更新序列化器
    用于更新现有记录时的验证
    """
    
    class Meta(WorkflowSchemeModelSerializer.Meta):
        read_only_fields = ["id", "scheme_info", "create_datetime", "update_datetime"]


class WorkflowSchemeModelListSerializer(WorkflowSchemeModelSerializer):
    """
    列表序列化器
    只包含列表展示需要的核心字段
    """
    
    # 关联字段 - 从 SchemeInfo 获取
    scheme_info_id = serializers.SerializerMethodField()
    scheme_code = serializers.SerializerMethodField()
    scheme_name = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    mark = serializers.SerializerMethodField()
    is_in_app = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowSchemeModel
        fields = [
            "id",
            "scheme_info_id",  # 保留ID字段便于前端使用
            "type",
            "type_display",
            "scheme_code",
            "scheme_name",
            "category",
            "mark",
            "is_in_app",
            "enabled_mark",
            "description",
            "creator_name",
            "create_datetime",
            "update_datetime",
        ]
        read_only_fields = fields
    
    def get_scheme_info_id(self, obj):
        """获取scheme_info的ID"""
        if obj.scheme_info:
            return str(obj.scheme_info.id)
        return None
    
    def get_scheme_code(self, obj):
        """获取流程编号"""
        if hasattr(obj, 'scheme_info') and obj.scheme_info:
            return obj.scheme_info.code
        return None
    
    def get_scheme_name(self, obj):
        """获取流程名称"""
        if hasattr(obj, 'scheme_info') and obj.scheme_info:
            return obj.scheme_info.name
        return None
    
    def get_category(self, obj):
        """获取流程分类"""
        if hasattr(obj, 'scheme_info') and obj.scheme_info:
            return obj.scheme_info.category
        return None
    
    def get_mark(self, obj):
        """获取是否允许发起"""
        if hasattr(obj, 'scheme_info') and obj.scheme_info:
            return obj.scheme_info.mark
        return None
    
    def get_is_in_app(self, obj):
        """获取是否在App上允许发起"""
        if hasattr(obj, 'scheme_info') and obj.scheme_info:
            return obj.scheme_info.is_in_app
        return None


class WorkflowSchemeModelImportSerializer(CustomModelSerializer):
    """
    导入序列化器
    用于Excel导入时的验证
    """
    
    class Meta:
        model = WorkflowSchemeModel
        fields = [
            'scheme_info_id',
            'type',
            'content',
        ]
        extra_kwargs = {
            'scheme_info_id': {'required': True},
            'type': {'required': True},
            'content': {'required': False, 'allow_null': True, 'allow_blank': True},
        }
    
    def validate_type(self, value):
        """验证模板类型"""
        if value not in [1, 2]:
            raise serializers.ValidationError("模板类型只能是1(正式)或2(草稿)")
        return value
