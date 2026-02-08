'''
Description: 任务消息序列化器
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import WorkflowTaskMsgModel


class WorkflowTaskMsgModelSerializer(CustomModelSerializer):
    """
    任务消息序列化器
    用于详情、更新等场景
    """
    
    # 计算字段 - 是否结束显示
    is_finished_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowTaskMsgModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "process_id": {"required": False, "allow_null": True, "allow_blank": True},
            "task_id": {"required": False, "allow_null": True, "allow_blank": True},
            "from_user_id": {"required": False, "allow_null": True, "allow_blank": True},
            "from_user_account": {"required": False, "allow_null": True, "allow_blank": True},
            "from_user_name": {"required": False, "allow_null": True, "allow_blank": True},
            "to_user_id": {"required": False, "allow_null": True, "allow_blank": True},
            "to_account": {"required": False, "allow_null": True, "allow_blank": True},
            "to_name": {"required": False, "allow_null": True, "allow_blank": True},
            "title": {"required": False, "allow_null": True, "allow_blank": True},
            "content": {"required": False, "allow_null": True, "allow_blank": True},
            "is_finished": {"required": False, "allow_null": True},
        }
    
    def get_is_finished_display(self, obj):
        """获取是否结束显示"""
        if obj.is_finished is None:
            return None
        return "结束" if obj.is_finished == 1 else "未结束"
    
    def validate_is_finished(self, value):
        """验证是否结束"""
        if value is not None and value not in [0, 1]:
            raise serializers.ValidationError("是否结束只能是0(未结束)或1(结束)")
        return value


class WorkflowTaskMsgModelCreateSerializer(WorkflowTaskMsgModelSerializer):
    """
    创建序列化器
    用于创建新记录时的验证
    """
    
    class Meta(WorkflowTaskMsgModelSerializer.Meta):
        extra_kwargs = {
            **WorkflowTaskMsgModelSerializer.Meta.extra_kwargs,
            "to_user_id": {"required": True},
            "title": {"required": True},
        }


class WorkflowTaskMsgModelUpdateSerializer(WorkflowTaskMsgModelSerializer):
    """
    更新序列化器
    用于更新现有记录时的验证
    """
    
    class Meta(WorkflowTaskMsgModelSerializer.Meta):
        read_only_fields = ["id", "process_id", "task_id", "from_user_id", "from_user_account", "from_user_name", "to_user_id", "to_account", "to_name", "create_datetime", "update_datetime"]


class WorkflowTaskMsgModelListSerializer(WorkflowTaskMsgModelSerializer):
    """
    列表序列化器
    只包含列表展示需要的核心字段
    """
    
    class Meta:
        model = WorkflowTaskMsgModel
        fields = [
            "id",
            "process_id",
            "task_id",
            "from_user_name",
            "to_user_id",
            "to_name",
            "title",
            "content",
            "is_finished",
            "is_finished_display",
            "create_datetime",
        ]
        read_only_fields = fields


class WorkflowTaskMsgModelImportSerializer(CustomModelSerializer):
    """
    导入序列化器
    用于Excel导入时的验证
    """
    
    class Meta:
        model = WorkflowTaskMsgModel
        fields = [
            'process_id',
            'task_id',
            'from_user_id',
            'from_user_name',
            'to_user_id',
            'to_name',
            'title',
            'content',
        ]
        extra_kwargs = {
            'process_id': {'required': False, 'allow_null': True, 'allow_blank': True},
            'task_id': {'required': False, 'allow_null': True, 'allow_blank': True},
            'from_user_id': {'required': False, 'allow_null': True, 'allow_blank': True},
            'from_user_name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'to_user_id': {'required': True},
            'to_name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'title': {'required': True},
            'content': {'required': False, 'allow_null': True, 'allow_blank': True},
        }

