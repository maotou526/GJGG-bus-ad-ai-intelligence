'''
Description: 任务消息视图
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework.decorators import action
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import WorkflowTaskMsgModel
from .serializers import (
    WorkflowTaskMsgModelSerializer,
    WorkflowTaskMsgModelCreateSerializer,
    WorkflowTaskMsgModelUpdateSerializer,
    WorkflowTaskMsgModelListSerializer,
    WorkflowTaskMsgModelImportSerializer,
)


class WorkflowTaskMsgModelViewSet(CustomModelViewSet):
    """
    任务消息管理视图集
    提供标准的 CRUD 接口和自定义业务接口
    """
    
    queryset = WorkflowTaskMsgModel.objects.all()
    serializer_class = WorkflowTaskMsgModelSerializer
    create_serializer_class = WorkflowTaskMsgModelCreateSerializer
    update_serializer_class = WorkflowTaskMsgModelUpdateSerializer
    list_serializer_class = WorkflowTaskMsgModelListSerializer
    import_serializer_class = WorkflowTaskMsgModelImportSerializer
    
    # 排序配置
    ordering_fields = ['process_id', 'task_id', 'create_datetime', 'update_datetime']
    ordering = ['-create_datetime']
    
    # 搜索字段
    search_fields = ['title', 'content', 'from_user_name', 'to_name']
    
    # 过滤字段
    filter_fields = ['id', 'process_id', 'task_id', 'to_user_id', 'is_finished']
    
    @action(methods=['GET'], detail=False, url_path='my-messages')
    def get_my_messages(self, request):
        """
        获取我的消息列表
        
        请求方式：GET /api/WorkflowTaskMsgModelViewSet/my-messages/
        
        请求参数：
            is_finished: 是否结束（可选，0=未结束, 1=结束）
            
        返回结果：
        {
            "code": 2000,
            "data": {
                "results": [...],
                "total": 10
            },
            "msg": "获取成功"
        }
        """
        user_id = request.user.id if hasattr(request.user, 'id') else None
        if not user_id:
            return ErrorResponse(msg="用户未登录")
        
        queryset = self.get_queryset().filter(to_user_id=str(user_id))
        
        # 过滤是否结束
        is_finished = request.query_params.get('is_finished', None)
        if is_finished is not None:
            queryset = queryset.filter(is_finished=int(is_finished))
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")
    
    @action(methods=['GET'], detail=False, url_path='by-process')
    def get_by_process(self, request):
        """
        根据流程ID获取消息列表
        
        请求方式：GET /api/WorkflowTaskMsgModelViewSet/by-process/
        
        请求参数：
            process_id: 流程ID
            
        返回结果：
        {
            "code": 2000,
            "data": [...],
            "msg": "获取成功"
        }
        """
        process_id = request.query_params.get('process_id', None)
        if not process_id:
            return ErrorResponse(msg="process_id 参数必填")
        
        queryset = self.get_queryset().filter(process_id=process_id).order_by('-create_datetime')
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")
