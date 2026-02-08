'''
Description: 流程模板权限序列化器
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import WorkflowSchemeAuthModel


class WorkflowSchemeAuthModelSerializer(CustomModelSerializer):
    """
    流程模板权限序列化器
    用于详情、更新等场景
    """
    
    # 计算字段 - 对象类型显示
    obj_type_display = serializers.SerializerMethodField()
    
    class Meta:
        model = WorkflowSchemeAuthModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "scheme_info_id": {"required": False, "allow_null": True, "allow_blank": True},
            "obj_type": {"required": True},
            "obj_id": {"required": False, "allow_null": True, "allow_blank": True},
            "obj_name": {"required": False, "allow_null": True, "allow_blank": True},
        }
    
    def get_obj_type_display(self, obj):
        """获取对象类型显示"""
        obj_type_map = {
            1: "岗位",
            2: "角色",
            3: "用户",
            4: "所有人可看",
        }
        return obj_type_map.get(obj.obj_type, "未知")
    
    def validate_obj_type(self, value):
        """验证对象类型"""
        if value not in [1, 2, 3, 4]:
            raise serializers.ValidationError("对象类型只能是1(岗位)、2(角色)、3(用户)或4(所有人可看)")
        return value
    
    def validate(self, attrs):
        """对象级验证"""
        attrs = super().validate(attrs)
        
        # obj_type=4时，obj_id应该为空
        obj_type = attrs.get('obj_type')
        obj_id = attrs.get('obj_id')
        
        if obj_type == 4 and obj_id:
            raise serializers.ValidationError("对象类型为4(所有人可看)时，对象ID必须为空")
        
        if obj_type in [1, 2, 3] and not obj_id:
            raise serializers.ValidationError(f"对象类型为{obj_type}时，对象ID不能为空")
        
        return attrs


class WorkflowSchemeAuthModelCreateSerializer(WorkflowSchemeAuthModelSerializer):
    """
    创建序列化器
    用于创建新记录时的验证
    """
    
    class Meta(WorkflowSchemeAuthModelSerializer.Meta):
        extra_kwargs = {
            **WorkflowSchemeAuthModelSerializer.Meta.extra_kwargs,
            "scheme_info_id": {"required": True},
            "obj_type": {"required": True},
        }


class WorkflowSchemeAuthModelUpdateSerializer(WorkflowSchemeAuthModelSerializer):
    """
    更新序列化器
    用于更新现有记录时的验证
    """
    
    class Meta(WorkflowSchemeAuthModelSerializer.Meta):
        read_only_fields = ["id", "scheme_info_id", "create_datetime", "update_datetime"]


class WorkflowSchemeAuthModelListSerializer(WorkflowSchemeAuthModelSerializer):
    """
    列表序列化器
    只包含列表展示需要的核心字段
    """
    
    class Meta:
        model = WorkflowSchemeAuthModel
        fields = [
            "id",
            "scheme_info_id",
            "obj_type",
            "obj_type_display",
            "obj_id",
            "obj_name",
            "create_datetime",
            "update_datetime",
        ]
        read_only_fields = fields


class WorkflowSchemeAuthModelImportSerializer(CustomModelSerializer):
    """
    导入序列化器
    用于Excel导入时的验证
    """
    
    class Meta:
        model = WorkflowSchemeAuthModel
        fields = [
            'scheme_info_id',
            'obj_type',
            'obj_id',
            'obj_name',
        ]
        extra_kwargs = {
            'scheme_info_id': {'required': True},
            'obj_type': {'required': True},
            'obj_id': {'required': False, 'allow_null': True, 'allow_blank': True},
            'obj_name': {'required': False, 'allow_null': True, 'allow_blank': True},
        }
    
    def validate_obj_type(self, value):
        """验证对象类型"""
        if value not in [1, 2, 3, 4]:
            raise serializers.ValidationError("对象类型只能是1(岗位)、2(角色)、3(用户)或4(所有人可看)")
        return value
    
    def validate(self, attrs):
        """对象级验证"""
        attrs = super().validate(attrs)
        
        obj_type = attrs.get('obj_type')
        obj_id = attrs.get('obj_id')
        
        if obj_type == 4 and obj_id:
            raise serializers.ValidationError("对象类型为4(所有人可看)时，对象ID必须为空")
        
        if obj_type in [1, 2, 3] and not obj_id:
            raise serializers.ValidationError(f"对象类型为{obj_type}时，对象ID不能为空")
        
        return attrs
