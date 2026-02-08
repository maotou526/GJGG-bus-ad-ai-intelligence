'''
Description: 任务执行人关系序列化器
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import WorkflowTaskRelationModel


class WorkflowTaskRelationModelSerializer(CustomModelSerializer):
    """
    任务执行人关系序列化器
    用于详情、更新等场景
    """
    
    # 计算字段 - 标记显示
    mark_display = serializers.SerializerMethodField()
    
    # 计算字段 - 处理结果显示
    result_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowTaskRelationModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "task_id": {"required": False, "allow_null": True, "allow_blank": True},
            "user_id": {"required": False, "allow_null": True, "allow_blank": True},
            "mark": {"required": False, "allow_null": True},
            "result": {"required": False, "allow_null": True},
            "sort": {"required": False, "allow_null": True},
            "time": {"required": False, "allow_null": True, "format": "%Y-%m-%d %H:%M:%S"},
        }
    
    def get_mark_display(self, obj):
        """获取标记显示"""
        if obj.mark is None:
            return None
        mark_map = {
            0: "需要处理",
            1: "暂时不需要处理",
        }
        return mark_map.get(obj.mark, "未知")
    
    def get_result_display(self, obj):
        """获取处理结果显示"""
        if obj.result is None or obj.result == 0:
            return "未处理"
        result_map = {
            1: "同意",
            2: "不同意",
        }
        return result_map.get(obj.result, "未知")
    
    def validate_mark(self, value):
        """验证标记"""
        if value is not None and value not in [0, 1]:
            raise serializers.ValidationError("标记只能是0(需要处理)或1(暂时不需要处理)")
        return value
    
    def validate_result(self, value):
        """验证处理结果"""
        if value is not None and value not in [0, 1, 2]:
            raise serializers.ValidationError("处理结果只能是0(未处理)、1(同意)或2(不同意)")
        return value


class WorkflowTaskRelationModelCreateSerializer(WorkflowTaskRelationModelSerializer):
    """
    创建序列化器
    用于创建新记录时的验证
    """
    
    class Meta(WorkflowTaskRelationModelSerializer.Meta):
        extra_kwargs = {
            **WorkflowTaskRelationModelSerializer.Meta.extra_kwargs,
            "task_id": {"required": True},
            "user_id": {"required": True},
        }


class WorkflowTaskRelationModelUpdateSerializer(WorkflowTaskRelationModelSerializer):
    """
    更新序列化器
    用于更新现有记录时的验证
    """
    
    class Meta(WorkflowTaskRelationModelSerializer.Meta):
        read_only_fields = ["id", "task_id", "user_id", "create_datetime", "update_datetime"]


class WorkflowTaskRelationModelListSerializer(WorkflowTaskRelationModelSerializer):
    """
    列表序列化器
    只包含列表展示需要的核心字段
    """
    
    class Meta:
        model = WorkflowTaskRelationModel
        fields = [
            "id",
            "task_id",
            "user_id",
            "mark",
            "mark_display",
            "result",
            "result_display",
            "sort",
            "time",
            "create_datetime",
            "update_datetime",
        ]
        read_only_fields = fields


class WorkflowTaskRelationModelImportSerializer(CustomModelSerializer):
    """
    导入序列化器
    用于Excel导入时的验证
    """
    
    class Meta:
        model = WorkflowTaskRelationModel
        fields = [
            'task_id',
            'user_id',
            'mark',
            'result',
            'sort',
        ]
        extra_kwargs = {
            'task_id': {'required': True},
            'user_id': {'required': True},
            'mark': {'required': False, 'allow_null': True},
            'result': {'required': False, 'allow_null': True},
            'sort': {'required': False, 'allow_null': True},
        }

