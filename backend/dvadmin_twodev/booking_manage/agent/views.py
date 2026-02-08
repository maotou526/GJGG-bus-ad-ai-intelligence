'''
Description: 代理商视图
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from rest_framework.decorators import action
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import AgentModel
from .serializers import (
    AgentModelSerializer,
    AgentModelCreateSerializer,
    AgentModelUpdateSerializer,
    AgentModelListSerializer
)
from django.db.models import Q


class AgentModelViewSet(CustomModelViewSet):
    """
    代理商管理视图集
    
    功能说明:
    - 提供代理商的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作
    
    标准DRF接口:
    - GET /api/AgentModelViewSet/ - 获取代理商列表
    - POST /api/AgentModelViewSet/ - 创建代理商
    - PUT /api/AgentModelViewSet/{id}/ - 更新代理商
    - DELETE /api/AgentModelViewSet/{id}/ - 删除代理商
    """
    # 查询集
    queryset = AgentModel.objects.all()
    
    # 默认序列化器(用于查询详情)
    serializer_class = AgentModelSerializer
    
    # 列表序列化器(用于列表展示)
    list_serializer_class = AgentModelListSerializer
    
    # 创建序列化器
    create_serializer_class = AgentModelCreateSerializer
    
    # 更新序列化器
    update_serializer_class = AgentModelUpdateSerializer
    
    # 过滤字段(支持精确查询)
    filter_fields = [
        'id', 'agent_code', 'company_name', 'credit_code',
        'cooperation_level', 'settlement_type', 'enabled_mark', 'delete_mark'
    ]
    
    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        'id', 'agent_code', 'company_name', 'credit_code',
        'cooperation_level', 'settlement_type', 'enabled_mark', 'delete_mark'
    ]
    
    # 搜索字段(支持模糊查询)
    search_fields = ['agent_code', 'company_name', 'credit_code', 'legal_person', 'contact_phone', 'contact_email']
    
    # 排序字段
    ordering_fields = ['agent_code', 'company_name', 'create_datetime', 'update_datetime', 'cooperation_level']
    
    # 默认排序
    ordering = ['company_name']
