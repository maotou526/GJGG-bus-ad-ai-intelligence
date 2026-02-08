'''
Description: 任务日志序列化器
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import WorkflowTaskLogModel


class WorkflowTaskLogModelSerializer(CustomModelSerializer):
    """
    任务日志序列化器
    用于详情、更新等场景
    """
    
    # 计算字段 - 流程任务类型显示
    task_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowTaskLogModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "process_id": {"required": False, "allow_null": True, "allow_blank": True},
            "task_id": {"required": False, "allow_null": True, "allow_blank": True},
            "operation_code": {"required": False, "allow_null": True, "allow_blank": True},
            "operation_name": {"required": False, "allow_null": True, "allow_blank": True},
            "node_id": {"required": False, "allow_null": True, "allow_blank": True},
            "node_name": {"required": False, "allow_null": True, "allow_blank": True},
            "task_type": {"required": True},
            "prev_node_id": {"required": False, "allow_null": True, "allow_blank": True},
            "prev_node_name": {"required": False, "allow_null": True, "allow_blank": True},
            "task_user_id": {"required": False, "allow_null": True, "allow_blank": True},
            "task_user_name": {"required": False, "allow_null": True, "allow_blank": True},
            "des": {"required": False, "allow_null": True, "allow_blank": True},
            "sign_img": {"required": False, "allow_null": True, "allow_blank": True},
            "stamp_img": {"required": False, "allow_null": True, "allow_blank": True},
        }
    
    def get_task_type_display(self, obj):
        """获取流程任务类型显示"""
        task_type_map = {
            0: "创建",
            1: "审批",
            2: "传阅",
            3: "加签审核",
            4: "子流程",
            5: "重新创建",
        }
        return task_type_map.get(obj.task_type, "未知")
    
    def validate_task_type(self, value):
        """验证流程任务类型"""
        if value not in [0, 1, 2, 3, 4, 5]:
            raise serializers.ValidationError("流程任务类型只能是0(创建)、1(审批)、2(传阅)、3(加签审核)、4(子流程)或5(重新创建)")
        return value


class WorkflowTaskLogModelCreateSerializer(WorkflowTaskLogModelSerializer):
    """
    创建序列化器
    用于创建新记录时的验证
    """
    
    class Meta(WorkflowTaskLogModelSerializer.Meta):
        extra_kwargs = {
            **WorkflowTaskLogModelSerializer.Meta.extra_kwargs,
            "process_id": {"required": True},
            "task_type": {"required": True},
        }


class WorkflowTaskLogModelUpdateSerializer(WorkflowTaskLogModelSerializer):
    """
    更新序列化器
    用于更新现有记录时的验证
    """
    
    class Meta(WorkflowTaskLogModelSerializer.Meta):
        read_only_fields = ["id", "process_id", "task_id", "create_datetime", "update_datetime"]


class WorkflowTaskLogModelListSerializer(WorkflowTaskLogModelSerializer):
    """
    列表序列化器
    只包含列表展示需要的核心字段
    """
    
    class Meta:
        model = WorkflowTaskLogModel
        fields = [
            "id",
            "process_id",
            "task_id",
            "operation_code",
            "operation_name",
            "node_id",
            "node_name",
            "task_type",
            "task_type_display",
            "prev_node_id",
            "prev_node_name",
            "creator_name",
            "task_user_name",
            "des",
            "create_datetime",
        ]
        read_only_fields = fields


class WorkflowTaskLogModelImportSerializer(CustomModelSerializer):
    """
    导入序列化器
    用于Excel导入时的验证
    """
    
    class Meta:
        model = WorkflowTaskLogModel
        fields = [
            'process_id',
            'task_id',
            'operation_code',
            'operation_name',
            'node_id',
            'node_name',
            'task_type',
            'des',
        ]
        extra_kwargs = {
            'process_id': {'required': True},
            'task_id': {'required': False, 'allow_null': True, 'allow_blank': True},
            'operation_code': {'required': False, 'allow_null': True, 'allow_blank': True},
            'operation_name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'node_id': {'required': False, 'allow_null': True, 'allow_blank': True},
            'node_name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'task_type': {'required': True},
            'des': {'required': False, 'allow_null': True, 'allow_blank': True},
        }

