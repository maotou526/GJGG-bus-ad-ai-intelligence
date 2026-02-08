'''
Description: 流程任务序列化器
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import WorkflowTaskModel


class WorkflowTaskModelSerializer(CustomModelSerializer):
    """
    流程任务序列化器
    用于详情、更新等场景
    """
    
    # 计算字段 - 任务类型显示
    type_display = serializers.SerializerMethodField()
    
    # 计算字段 - 是否完成显示
    is_finished_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowTaskModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "process_id": {"required": False, "allow_null": True, "allow_blank": True},
            "node_id": {"required": False, "allow_null": True, "allow_blank": True},
            "node_name": {"required": False, "allow_null": True, "allow_blank": True},
            "type": {"required": True},
            "is_finished": {"required": True},
            "timeout_action": {"required": False, "allow_null": True},
            "timeout_notice": {"required": False, "allow_null": True},
            "timeout_interval": {"required": False, "allow_null": True},
            "timeout_strategy": {"required": False, "allow_null": True, "allow_blank": True},
            "prev_node_id": {"required": False, "allow_null": True, "allow_blank": True},
            "prev_node_name": {"required": False, "allow_null": True, "allow_blank": True},
            "is_urge": {"required": False, "allow_null": True},
            "first_user_id": {"required": False, "allow_null": True, "allow_blank": True},
            "child_process_id": {"required": False, "allow_null": True, "allow_blank": True},
            "is_batch_audit": {"required": False, "allow_null": True},
            "is_next_audit": {"required": False, "allow_null": True},
        }
    
    def get_type_display(self, obj):
        """获取任务类型显示"""
        type_map = {
            1: "审批",
            2: "传阅",
            3: "加签",
            4: "子流程",
            5: "重新创建",
        }
        return type_map.get(obj.type, "未知")
    
    def get_is_finished_display(self, obj):
        """获取是否完成显示"""
        finished_map = {
            0: "未完成",
            1: "完成",
            2: "关闭",
        }
        return finished_map.get(obj.is_finished, "未知")
    
    def validate_type(self, value):
        """验证任务类型"""
        if value not in [1, 2, 3, 4, 5]:
            raise serializers.ValidationError("任务类型只能是1(审批)、2(传阅)、3(加签)、4(子流程)或5(重新创建)")
        return value
    
    def validate_is_finished(self, value):
        """验证是否完成"""
        if value not in [0, 1, 2]:
            raise serializers.ValidationError("是否完成只能是0(未完成)、1(完成)或2(关闭)")
        return value


class WorkflowTaskModelCreateSerializer(WorkflowTaskModelSerializer):
    """
    创建序列化器
    用于创建新记录时的验证
    """
    
    class Meta(WorkflowTaskModelSerializer.Meta):
        extra_kwargs = {
            **WorkflowTaskModelSerializer.Meta.extra_kwargs,
            "process_id": {"required": True},
            "node_id": {"required": True},
            "type": {"required": True},
            "is_finished": {"required": True},
        }


class WorkflowTaskModelUpdateSerializer(WorkflowTaskModelSerializer):
    """
    更新序列化器
    用于更新现有记录时的验证
    """
    
    class Meta(WorkflowTaskModelSerializer.Meta):
        read_only_fields = ["id", "process_id", "node_id", "create_datetime", "update_datetime"]


class WorkflowTaskModelListSerializer(WorkflowTaskModelSerializer):
    """
    列表序列化器
    只包含列表展示需要的核心字段
    """
    
    class Meta:
        model = WorkflowTaskModel
        fields = [
            "id",
            "process_id",
            "node_id",
            "node_name",
            "type",
            "type_display",
            "is_finished",
            "is_finished_display",
            "prev_node_id",
            "prev_node_name",
            "is_batch_audit",
            "creator_name",
            "modifier_name",
            "create_datetime",
            "update_datetime",
        ]
        read_only_fields = fields


class WorkflowTaskModelImportSerializer(CustomModelSerializer):
    """
    导入序列化器
    用于Excel导入时的验证
    """
    
    class Meta:
        model = WorkflowTaskModel
        fields = [
            'process_id',
            'node_id',
            'node_name',
            'type',
            'is_finished',
        ]
        extra_kwargs = {
            'process_id': {'required': True},
            'node_id': {'required': True},
            'node_name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'type': {'required': True},
            'is_finished': {'required': True},
        }

