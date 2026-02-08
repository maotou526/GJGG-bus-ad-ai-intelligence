'''
Description: 客户视图
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from rest_framework.decorators import action
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import CustomerModel
from .serializers import (
    CustomerModelSerializer,
    CustomerModelCreateSerializer,
    CustomerModelUpdateSerializer,
    CustomerModelListSerializer
)
from django.db.models import Q


class CustomerModelViewSet(CustomModelViewSet):
    """
    客户管理视图集
    
    功能说明:
    - 提供客户的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作
    
    标准DRF接口:
    - GET /api/CustomerModelViewSet/ - 获取客户列表
    - POST /api/CustomerModelViewSet/ - 创建客户
    - PUT /api/CustomerModelViewSet/{id}/ - 更新客户
    - DELETE /api/CustomerModelViewSet/{id}/ - 删除客户
    """
    # 查询集
    queryset = CustomerModel.objects.all()
    
    # 默认序列化器(用于查询详情)
    serializer_class = CustomerModelSerializer
    
    # 列表序列化器(用于列表展示)
    list_serializer_class = CustomerModelListSerializer
    
    # 创建序列化器
    create_serializer_class = CustomerModelCreateSerializer
    
    # 更新序列化器
    update_serializer_class = CustomerModelUpdateSerializer
    
    # 过滤字段(支持精确查询)
    filter_fields = [
        'id', 'customer_code', 'company_name', 'credit_code',
        'agent_id', 'industry', 'customer_level', 'status', 'enabled_mark', 'delete_mark'
    ]
    
    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        'id', 'customer_code', 'company_name', 'credit_code',
        'agent_id', 'industry', 'customer_level', 'status', 'enabled_mark', 'delete_mark'
    ]
    
    # 搜索字段(支持模糊查询)
    search_fields = ['customer_code', 'company_name', 'credit_code', 'contact_name', 'contact_phone', 'contact_email']
    
    # 排序字段
    ordering_fields = ['customer_code', 'company_name', 'create_datetime', 'update_datetime', 'customer_level', 'status']
    
    # 默认排序
    ordering = ['company_name']
