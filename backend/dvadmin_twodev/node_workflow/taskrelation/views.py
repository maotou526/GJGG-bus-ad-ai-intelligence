'''
Description: 任务执行人关系视图
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework.decorators import action
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import WorkflowTaskRelationModel
from .serializers import (
    WorkflowTaskRelationModelSerializer,
    WorkflowTaskRelationModelCreateSerializer,
    WorkflowTaskRelationModelUpdateSerializer,
    WorkflowTaskRelationModelListSerializer,
    WorkflowTaskRelationModelImportSerializer,
)


class WorkflowTaskRelationModelViewSet(CustomModelViewSet):
    """
    任务执行人关系管理视图集
    提供标准的 CRUD 接口和自定义业务接口
    """
    
    queryset = WorkflowTaskRelationModel.objects.all()
    serializer_class = WorkflowTaskRelationModelSerializer
    create_serializer_class = WorkflowTaskRelationModelCreateSerializer
    update_serializer_class = WorkflowTaskRelationModelUpdateSerializer
    list_serializer_class = WorkflowTaskRelationModelListSerializer
    import_serializer_class = WorkflowTaskRelationModelImportSerializer
    
    # 排序配置
    ordering_fields = ['task_id', 'user_id', 'sort', 'time', 'create_datetime', 'update_datetime']
    ordering = ['-create_datetime']
    
    # 搜索字段
    search_fields = ['task_id', 'user_id']
    
    # 过滤字段
    filter_fields = ['id', 'task_id', 'user_id', 'mark', 'result']
    
    @action(methods=['GET'], detail=False, url_path='by-task')
    def get_by_task(self, request):
        """
        根据任务ID获取执行人列表
        
        请求方式：GET /api/WorkflowTaskRelationModelViewSet/by-task/
        
        请求参数：
            task_id: 任务ID
            
        返回结果：
        {
            "code": 2000,
            "data": [
                {
                    "id": "...",
                    "task_id": "...",
                    "user_id": "...",
                    "mark": 0,
                    "result": 1,
                    ...
                }
            ],
            "msg": "获取成功"
        }
        """
        task_id = request.query_params.get('task_id', None)
        if not task_id:
            return ErrorResponse(msg="task_id 参数必填")
        
        queryset = self.get_queryset().filter(task_id=task_id).order_by('sort', 'create_datetime')
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")
    
    @action(methods=['GET'], detail=False, url_path='by-user')
    def get_by_user(self, request):
        """
        根据用户ID获取任务关系列表
        
        请求方式：GET /api/WorkflowTaskRelationModelViewSet/by-user/
        
        请求参数：
            user_id: 用户ID
            mark: 标记（可选，0=需要处理, 1=暂时不需要处理）
            
        返回结果：
        {
            "code": 2000,
            "data": [...],
            "msg": "获取成功"
        }
        """
        user_id = request.query_params.get('user_id', None)
        if not user_id:
            return ErrorResponse(msg="user_id 参数必填")
        
        queryset = self.get_queryset().filter(user_id=user_id)
        
        # 过滤标记
        mark = request.query_params.get('mark', None)
        if mark is not None:
            queryset = queryset.filter(mark=int(mark))
        
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")
