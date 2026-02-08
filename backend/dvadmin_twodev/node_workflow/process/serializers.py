'''
Description: 流程进程序列化器
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import WorkflowProcessModel


class WorkflowProcessModelSerializer(CustomModelSerializer):
    """
    流程进程序列化器
    用于详情、更新等场景
    """
    
    # 计算字段 - 流程进程等级显示
    level_display = serializers.SerializerMethodField()
    
    # 计算字段 - 流程进程有效标志显示
    enabled_mark_display = serializers.SerializerMethodField()
    
    # 计算字段 - 是否重新发起显示
    is_again_display = serializers.SerializerMethodField()
    
    # 计算字段 - 是否结束显示
    is_finished_display = serializers.SerializerMethodField()
    
    # 计算字段 - 是否是子流程显示
    is_child_display = serializers.SerializerMethodField()
    
    # 计算字段 - 子流程执行方式显示
    is_asyn_display = serializers.SerializerMethodField()
    
    # 计算字段 - 是否开始处理显示
    is_start_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowProcessModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "scheme_id": {"required": False, "allow_null": True, "allow_blank": True},
            "scheme_code": {"required": False, "allow_null": True, "allow_blank": True},
            "scheme_name": {"required": False, "allow_null": True, "allow_blank": True},
            "title": {"required": False, "allow_null": True, "allow_blank": True},
            "level": {"required": False, "allow_null": True},
            "is_again": {"required": True},
            "is_finished": {"required": True},
            "is_child": {"required": True},
            "is_asyn": {"required": False, "allow_null": True},
            "parent_node_id": {"required": False, "allow_null": True, "allow_blank": True},
            "parent_task_id": {"required": False, "allow_null": True, "allow_blank": True},
            "parent_process_id": {"required": False, "allow_null": True, "allow_blank": True},
            "is_start": {"required": False, "allow_null": True},
        }
    
    def get_level_display(self, obj):
        """获取流程进程等级显示"""
        level_map = {
            1: "普通",
            2: "重要",
            3: "紧急",
        }
        return level_map.get(obj.level, "未知")
    
    def get_enabled_mark_display(self, obj):
        """获取流程进程有效标志显示"""
        enabled_mark_map = {
            1: "正常",
            2: "草稿",
            3: "作废",
        }
        return enabled_mark_map.get(obj.enabled_mark, "未知")
    
    def get_is_again_display(self, obj):
        """获取是否重新发起显示"""
        return "是" if obj.is_again == 1 else "不是"
    
    def get_is_finished_display(self, obj):
        """获取是否结束显示"""
        return "是" if obj.is_finished == 1 else "不是"
    
    def get_is_child_display(self, obj):
        """获取是否是子流程显示"""
        return "是" if obj.is_child == 1 else "不是"
    
    def get_is_asyn_display(self, obj):
        """获取子流程执行方式显示"""
        if obj.is_asyn is None:
            return None
        return "异步" if obj.is_asyn == 1 else "同步"
    
    def get_is_start_display(self, obj):
        """获取是否开始处理显示"""
        if obj.is_start is None:
            return None
        return "已开始" if obj.is_start == 1 else "未开始"
    
    def validate_level(self, value):
        """验证流程进程等级"""
        if value is not None and value not in [1, 2, 3]:
            raise serializers.ValidationError("流程进程等级只能是1(普通)、2(重要)或3(紧急)")
        return value
    
    def validate_enabled_mark(self, value):
        """验证流程进程有效标志"""
        if value is not None and value not in [1, 2, 3]:
            raise serializers.ValidationError("流程进程有效标志只能是1(正常)、2(草稿)或3(作废)")
        return value
    
    def validate_is_again(self, value):
        """验证是否重新发起"""
        if value not in [0, 1]:
            raise serializers.ValidationError("是否重新发起只能是0(不是)或1(是)")
        return value
    
    def validate_is_finished(self, value):
        """验证是否结束"""
        if value not in [0, 1]:
            raise serializers.ValidationError("是否结束只能是0(不是)或1(是)")
        return value
    
    def validate_is_child(self, value):
        """验证是否是子流程"""
        if value not in [0, 1]:
            raise serializers.ValidationError("是否是子流程只能是0(不是)或1(是)")
        return value
    
    def validate_is_asyn(self, value):
        """验证子流程执行方式"""
        if value is not None and value not in [0, 1]:
            raise serializers.ValidationError("子流程执行方式只能是0(同步)或1(异步)")
        return value


class WorkflowProcessModelCreateSerializer(WorkflowProcessModelSerializer):
    """
    创建序列化器
    用于创建新记录时的验证
    """
    
    class Meta(WorkflowProcessModelSerializer.Meta):
        extra_kwargs = {
            **WorkflowProcessModelSerializer.Meta.extra_kwargs,
            "scheme_id": {"required": True},
            "title": {"required": True},
        }


class WorkflowProcessModelUpdateSerializer(WorkflowProcessModelSerializer):
    """
    更新序列化器
    用于更新现有记录时的验证
    """
    
    class Meta(WorkflowProcessModelSerializer.Meta):
        read_only_fields = ["id", "scheme_id", "scheme_code", "scheme_name", "create_datetime", "update_datetime"]


class WorkflowProcessModelListSerializer(WorkflowProcessModelSerializer):
    """
    列表序列化器
    只包含列表展示需要的核心字段
    """
    
    class Meta:
        model = WorkflowProcessModel
        fields = [
            "id",
            "scheme_id",
            "scheme_code",
            "scheme_name",
            "title",
            "level",
            "level_display",
            "enabled_mark",
            "enabled_mark_display",
            "is_again",
            "is_again_display",
            "is_finished",
            "is_finished_display",
            "is_child",
            "is_child_display",
            "is_start",
            "is_start_display",
            "creator_name",
            "create_datetime",
            "update_datetime",
        ]
        read_only_fields = fields


class WorkflowProcessModelImportSerializer(CustomModelSerializer):
    """
    导入序列化器
    用于Excel导入时的验证
    """
    
    class Meta:
        model = WorkflowProcessModel
        fields = [
            'scheme_code',
            'scheme_name',
            'title',
            'level',
            'enabled_mark',
            'is_again',
            'is_finished',
            'is_child',
        ]
        extra_kwargs = {
            'scheme_code': {'required': True},
            'scheme_name': {'required': True},
            'title': {'required': True},
            'level': {'required': False, 'allow_null': True},
            'enabled_mark': {'required': True},
            'is_again': {'required': True},
            'is_finished': {'required': True},
            'is_child': {'required': True},
        }
