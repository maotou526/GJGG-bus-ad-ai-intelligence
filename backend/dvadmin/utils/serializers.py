# -*- coding: utf-8 -*-

"""
@author: 猿小天
@contact: QQ:1638245306
@Created on: 2021/6/1 001 22:47
@Remark: 自定义序列化器
"""
from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.request import Request
from rest_framework.serializers import ModelSerializer
from django.utils.functional import cached_property
from rest_framework.utils.serializer_helpers import BindingDict

from dvadmin.system.models import Users
from django_restql.mixins import DynamicFieldsMixin


class CustomModelSerializer(DynamicFieldsMixin, ModelSerializer):
    """
    增强DRF的ModelSerializer,可自动更新模型的审计字段记录
    (1)self.request能获取到rest_framework.request.Request对象
    """

    # 修改人的审计字段名称, 默认modifier, 继承使用时可自定义覆盖
    modifier_field_id = "modifier"
    modifier_name = serializers.SerializerMethodField(read_only=True)

    def get_modifier_name(self, instance):
        """获取修改人姓名"""
        # 优先从冗余字段读取（BaseDataModel提供）
        if hasattr(instance, 'modifier_name') and instance.modifier_name:
            return instance.modifier_name
        
        # 如果没有冗余字段，从外键关联读取
        try:
            if hasattr(instance, 'modifier') and instance.modifier:
                return getattr(instance.modifier, 'name', None)
        except Exception:
            # 如果关联的用户不存在或查询失败，返回 None
            return None
        
        return None

    # 创建人的审计字段名称, 默认creator, 继承使用时可自定义覆盖
    creator_field_id = "creator"
    creator_name = serializers.SerializerMethodField(read_only=True)
    
    def get_creator_name(self, instance):
        """获取创建人姓名"""
        # 优先从冗余字段读取
        if hasattr(instance, 'creator_name') and instance.creator_name:
            return instance.creator_name
        
        # 如果没有冗余字段，从外键关联读取
        try:
            if hasattr(instance, 'creator') and instance.creator:
                return getattr(instance.creator, 'name', None)
        except Exception:
            # 如果关联的用户不存在或查询失败，返回 None
            return None
        
        return None
    # 数据所属部门字段
    dept_belong_id_field_name = "dept_belong_id"
    # 添加默认时间返回格式
    create_datetime = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", required=False, read_only=True
    )
    update_datetime = serializers.DateTimeField(
        format="%Y-%m-%d %H:%M:%S", required=False, read_only=True
    )

    def __init__(self, instance=None, data=empty, request=None, **kwargs):
        super().__init__(instance, data, **kwargs)
        self.request: Request = request or self.context.get("request", None)

    def save(self, **kwargs):
        return super().save(**kwargs)

    def create(self, validated_data):
        """创建时自动填充审计字段"""
        if self.request and str(self.request.user) != "AnonymousUser":
            # 填充 creator（外键对象）
            if self.creator_field_id in self.fields.fields:
                validated_data[self.creator_field_id] = self.request.user
            
            # 填充 creator_name（冗余字段，BaseDataModel提供）
            if 'creator_name' in [f.name for f in self.Meta.model._meta.get_fields()]:
                validated_data['creator_name'] = getattr(self.request.user, 'name', '')
            
            # 填充 modifier（外键对象）
            if self.modifier_field_id in self.fields.fields:
                validated_data[self.modifier_field_id] = self.request.user
            
            # 填充 modifier_name（冗余字段，BaseDataModel提供）
            if 'modifier_name' in [f.name for f in self.Meta.model._meta.get_fields()]:
                validated_data['modifier_name'] = getattr(self.request.user, 'name', '')
            
            # 填充部门
            if (
                self.dept_belong_id_field_name in self.fields.fields
                and validated_data.get(self.dept_belong_id_field_name, None) is None
            ):
                validated_data[self.dept_belong_id_field_name] = getattr(
                    self.request.user, "dept_id", validated_data.get(self.dept_belong_id_field_name, None)
                )

            # 填充 company_belong_id（如果模型有此字段且未传值）
            model_field_names = [f.name for f in self.Meta.model._meta.get_fields()]
            if 'company_belong_id' in model_field_names:
                if validated_data.get('company_belong_id') is None:
                    validated_data['company_belong_id'] = getattr(self.request.user, 'company_belong_id', None)

            # 填充 agent_id（如果模型有此字段且未传值）
            if 'agent_id' in model_field_names:
                if validated_data.get('agent_id') is None:
                    validated_data['agent_id'] = getattr(self.request.user, 'agent_id', None)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """更新时自动填充审计字段"""
        if self.request and str(self.request.user) != "AnonymousUser":
            # 填充 modifier（外键对象）
            if self.modifier_field_id in self.fields.fields:
                validated_data[self.modifier_field_id] = self.request.user
            
            # 填充 modifier_name（冗余字段，BaseDataModel提供）
            if 'modifier_name' in [f.name for f in self.Meta.model._meta.get_fields()]:
                validated_data['modifier_name'] = getattr(self.request.user, 'name', '')
            
            # 同时更新实例属性
            # if hasattr(self.instance, self.modifier_field_id):
            #     setattr(self.instance, self.modifier_field_id, self.request.user)
            
            # if hasattr(self.instance, 'modifier_name'):
            #     setattr(self.instance, 'modifier_name', getattr(self.request.user, 'name', ''))
        
        return super().update(instance, validated_data)

    def get_request_username(self):
        if getattr(self.request, "user", None):
            return getattr(self.request.user, "username", None)
        return None

    def get_request_name(self):
        if getattr(self.request, "user", None):
            return getattr(self.request.user, "name", None)
        return None

    def get_request_user_id(self):
        if getattr(self.request, "user", None):
            return getattr(self.request.user, "id", None)
        return None

    @property
    def errors(self):
        # get errors
        errors = super().errors
        verbose_errors = {}

        # fields = { field.name: field.verbose_name } for each field in model
        fields = {field.name: field.verbose_name for field in
                  self.Meta.model._meta.get_fields() if hasattr(field, 'verbose_name')}

        # iterate over errors and replace error key with verbose name if exists
        for field_name, error in errors.items():
            if field_name in fields:
                verbose_errors[str(fields[field_name])] = error
            else:
                verbose_errors[field_name] = error
        return verbose_errors

    # @cached_property
    # def fields(self):
    #     fields = BindingDict(self)
    #     for key, value in self.get_fields().items():
    #         fields[key] = value
    #
    #     if not hasattr(self, '_context'):
    #         return fields
    #     is_root = self.root == self
    #     parent_is_list_root = self.parent == self.root and getattr(self.parent, 'many', False)
    #     if not (is_root or parent_is_list_root):
    #         return fields
    #
    #     try:
    #         request = self.request or self.context['request']
    #     except KeyError:
    #         return fields
    #     params = getattr(
    #         request, 'query_params', getattr(request, 'GET', None)
    #     )
    #     if params is None:
    #         pass
    #     try:
    #         filter_fields = params.get('_fields', None).split(',')
    #     except AttributeError:
    #         filter_fields = None
    #
    #     try:
    #         omit_fields = params.get('_exclude', None).split(',')
    #     except AttributeError:
    #         omit_fields = []
    #
    #     existing = set(fields.keys())
    #     if filter_fields is None:
    #         allowed = existing
    #     else:
    #         allowed = set(filter(None, filter_fields))
    #
    #     omitted = set(filter(None, omit_fields))
    #     for field in existing:
    #         if field not in allowed:
    #             fields.pop(field, None)
    #         if field in omitted:
    #             fields.pop(field, None)
    #
    #     return fields
