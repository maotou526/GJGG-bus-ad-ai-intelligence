'''
Description: 流程模板信息序列化器
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import WorkflowSchemeInfoModel


class WorkflowSchemeInfoModelSerializer(CustomModelSerializer):
    """
    流程模板信息序列化器
    用于详情、更新等场景
    """
    
    # 计算字段 - 是否允许发起显示
    mark_display = serializers.SerializerMethodField()
    
    # 计算字段 - 是否在App上允许发起显示
    is_in_app_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowSchemeInfoModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "code": {"required": False, "allow_null": True, "allow_blank": True},
            "name": {"required": False, "allow_null": True, "allow_blank": True},
            "category": {"required": False, "allow_null": True, "allow_blank": True},
            "scheme_id": {"required": False, "allow_null": True, "allow_blank": True},
            "mark": {"required": False, "allow_null": True},
            "is_in_app": {"required": False, "allow_null": True},
            "description": {"required": False, "allow_null": True, "allow_blank": True},
        }
    
    def get_mark_display(self, obj):
        """获取是否允许发起显示"""
        mark_map = {
            1: "允许",
            2: "不允许",
        }
        return mark_map.get(obj.mark, "未知")
    
    def get_is_in_app_display(self, obj):
        """获取是否在App上允许发起显示"""
        app_map = {
            1: "允许",
            2: "不允许",
        }
        return app_map.get(obj.is_in_app, "未知")
    
    def validate_code(self, value):
        """验证流程编号"""
        if value and value.strip():
            return value.strip()
        return value
    
    def validate_name(self, value):
        """验证流程名称"""
        if value and value.strip():
            return value.strip()
        return value


class WorkflowSchemeInfoModelCreateSerializer(WorkflowSchemeInfoModelSerializer):
    """
    创建序列化器
    用于创建新记录时的验证
    """
    
    class Meta(WorkflowSchemeInfoModelSerializer.Meta):
        extra_kwargs = {
            **WorkflowSchemeInfoModelSerializer.Meta.extra_kwargs,
            "code": {"required": True},
            "name": {"required": True},
            "mark": {"required": True},
            "is_in_app": {"required": True},
        }


class WorkflowSchemeInfoModelUpdateSerializer(WorkflowSchemeInfoModelSerializer):
    """
    更新序列化器
    用于更新现有记录时的验证
    """
    
    class Meta(WorkflowSchemeInfoModelSerializer.Meta):
        read_only_fields = ["id", "code", "create_datetime", "update_datetime"]


class WorkflowSchemeInfoModelListSerializer(WorkflowSchemeInfoModelSerializer):
    """
    列表序列化器
    只包含列表展示需要的核心字段
    """
    
    class Meta:
        model = WorkflowSchemeInfoModel
        fields = [
            "id",
            "code",
            "name",
            "category",
            "scheme_id",
            "mark",
            "mark_display",
            "is_in_app",
            "is_in_app_display",
            "enabled_mark",
            "description",
            "create_datetime",
            "update_datetime",
        ]
        read_only_fields = fields


class WorkflowSchemeInfoModelImportSerializer(CustomModelSerializer):
    """
    导入序列化器
    用于Excel导入时的验证
    """
    
    class Meta:
        model = WorkflowSchemeInfoModel
        fields = [
            'code',
            'name',
            'category',
            'mark',
            'is_in_app',
            'description',
        ]
        extra_kwargs = {
            'code': {'required': True},
            'name': {'required': True},
            'category': {'required': False, 'allow_null': True, 'allow_blank': True},
            'mark': {'required': True},
            'is_in_app': {'required': True},
            'description': {'required': False, 'allow_null': True, 'allow_blank': True},
        }

