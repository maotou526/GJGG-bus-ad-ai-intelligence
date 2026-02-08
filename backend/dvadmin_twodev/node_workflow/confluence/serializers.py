'''
Description: 会签序列化器
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import WorkflowConfluenceModel


class WorkflowConfluenceModelSerializer(CustomModelSerializer):
    """
    会签序列化器
    用于详情、更新等场景
    """
    
    # 计算字段 - 状态显示
    state_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowConfluenceModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "process_id": {"required": False, "allow_null": True, "allow_blank": True},
            "node_id": {"required": False, "allow_null": True, "allow_blank": True},
            "form_node_id": {"required": False, "allow_null": True, "allow_blank": True},
            "state": {"required": True},
        }
    
    def get_state_display(self, obj):
        """获取状态显示"""
        state_map = {
            1: "同意",
            0: "不同意",
        }
        return state_map.get(obj.state, "待处理")
    
    def validate_state(self, value):
        """验证状态"""
        if value is not None and value not in [0, 1]:
            raise serializers.ValidationError("状态只能是0(不同意)或1(同意)")
        return value


class WorkflowConfluenceModelCreateSerializer(WorkflowConfluenceModelSerializer):
    """
    创建序列化器
    用于创建新记录时的验证
    """
    
    class Meta(WorkflowConfluenceModelSerializer.Meta):
        extra_kwargs = {
            **WorkflowConfluenceModelSerializer.Meta.extra_kwargs,
            "process_id": {"required": True},
            "node_id": {"required": True},
            "state": {"required": True},
        }


class WorkflowConfluenceModelUpdateSerializer(WorkflowConfluenceModelSerializer):
    """
    更新序列化器
    用于更新现有记录时的验证
    """
    
    class Meta(WorkflowConfluenceModelSerializer.Meta):
        read_only_fields = ["id", "process_id", "node_id", "create_datetime", "update_datetime"]


class WorkflowConfluenceModelListSerializer(WorkflowConfluenceModelSerializer):
    """
    列表序列化器
    只包含列表展示需要的核心字段
    """
    
    class Meta:
        model = WorkflowConfluenceModel
        fields = [
            "id",
            "process_id",
            "node_id",
            "form_node_id",
            "state",
            "state_display",
            "create_datetime",
            "update_datetime",
        ]
        read_only_fields = fields


class WorkflowConfluenceModelImportSerializer(CustomModelSerializer):
    """
    导入序列化器
    用于Excel导入时的验证
    """
    
    class Meta:
        model = WorkflowConfluenceModel
        fields = [
            'process_id',
            'node_id',
            'form_node_id',
            'state',
        ]
        extra_kwargs = {
            'process_id': {'required': True},
            'node_id': {'required': True},
            'form_node_id': {'required': False, 'allow_null': True, 'allow_blank': True},
            'state': {'required': True},
        }
    
    def validate_state(self, value):
        """验证状态"""
        if value is not None and value not in [0, 1]:
            raise serializers.ValidationError("状态只能是0(不同意)或1(同意)")
        return value

