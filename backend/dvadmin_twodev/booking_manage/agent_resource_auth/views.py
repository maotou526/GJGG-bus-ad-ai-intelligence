'''
Description: 代理商资源授权视图
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from rest_framework.decorators import action
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import AgentResourceAuthModel
from .serializers import (
    AgentResourceAuthModelSerializer,
    AgentResourceAuthModelCreateSerializer,
    AgentResourceAuthModelUpdateSerializer,
    AgentResourceAuthModelListSerializer
)
from django.db.models import Q


class AgentResourceAuthModelViewSet(CustomModelViewSet):
    """
    代理商资源授权管理视图集
    
    功能说明:
    - 提供资源授权的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作
    
    标准DRF接口:
    - GET /api/AgentResourceAuthModelViewSet/ - 获取授权列表
    - POST /api/AgentResourceAuthModelViewSet/ - 创建授权
    - PUT /api/AgentResourceAuthModelViewSet/{id}/ - 更新授权
    - DELETE /api/AgentResourceAuthModelViewSet/{id}/ - 删除授权
    """
    # 查询集
    queryset = AgentResourceAuthModel.objects.all()
    
    # 默认序列化器(用于查询详情)
    serializer_class = AgentResourceAuthModelSerializer
    
    # 列表序列化器(用于列表展示)
    list_serializer_class = AgentResourceAuthModelListSerializer
    
    # 创建序列化器
    create_serializer_class = AgentResourceAuthModelCreateSerializer
    
    # 更新序列化器
    update_serializer_class = AgentResourceAuthModelUpdateSerializer
    
    # 过滤字段(支持精确查询)
    filter_fields = [
        'id', 'agent_id', 'resource_type', 'resource_id',
        'enabled_mark', 'delete_mark'
    ]
    
    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        'id', 'agent_id', 'resource_type', 'resource_id',
        'enabled_mark', 'delete_mark'
    ]
    
    # 搜索字段(支持模糊查询)
    search_fields = []
    
    # 排序字段
    ordering_fields = ['agent_id', 'resource_type', 'resource_id', 'create_datetime', 'update_datetime', 'auth_start_date', 'auth_end_date']
    
    # 默认排序
    ordering = ['agent_id', 'resource_type', 'resource_id']

    def get_queryset(self):
        """
        自定义查询集
        优化查询性能，预加载关联对象
        """
        queryset = super().get_queryset()
        
        # 使用 select_related 预加载关联对象，提高查询性能
        # 避免 N+1 查询问题
        queryset = queryset.select_related('agent_id')
        
        return queryset

    @action(detail=False, methods=['get'])
    def get_by_agent(self, request):
        """
        根据代理商ID获取授权列表
        GET /api/AgentResourceAuthModelViewSet/get_by_agent/?agent_id=1
        """
        agent_id = request.query_params.get('agent_id')
        if not agent_id:
            return ErrorResponse(message="代理商ID不能为空")
        
        try:
            agent_id = int(agent_id)
        except ValueError:
            return ErrorResponse(message="代理商ID格式错误")
        
        queryset = self.queryset.filter(agent_id=agent_id, delete_mark=0)
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")
