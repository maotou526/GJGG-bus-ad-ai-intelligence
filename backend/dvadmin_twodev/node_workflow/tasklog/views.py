'''
Description: 任务日志视图
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework.decorators import action
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import WorkflowTaskLogModel
from .serializers import (
    WorkflowTaskLogModelSerializer,
    WorkflowTaskLogModelCreateSerializer,
    WorkflowTaskLogModelUpdateSerializer,
    WorkflowTaskLogModelListSerializer,
    WorkflowTaskLogModelImportSerializer,
)


class WorkflowTaskLogModelViewSet(CustomModelViewSet):
    """
    任务日志管理视图集
    提供标准的 CRUD 接口和自定义业务接口
    """
    
    queryset = WorkflowTaskLogModel.objects.all()
    serializer_class = WorkflowTaskLogModelSerializer
    create_serializer_class = WorkflowTaskLogModelCreateSerializer
    update_serializer_class = WorkflowTaskLogModelUpdateSerializer
    list_serializer_class = WorkflowTaskLogModelListSerializer
    import_serializer_class = WorkflowTaskLogModelImportSerializer
    
    # 排序配置
    ordering_fields = ['process_id', 'task_id', 'create_datetime', 'update_datetime']
    ordering = ['-create_datetime']
    
    # 搜索字段
    search_fields = ['operation_name', 'node_name', 'creator_name', 'task_user_name', 'des']
    
    # 过滤字段
    filter_fields = ['id', 'process_id', 'task_id', 'task_type', 'operation_code', 'node_id']
    
    @action(methods=['GET'], detail=False, url_path='by-process')
    def get_by_process(self, request):
        """
        根据流程ID获取日志列表（用于生成流程审批时间轴）
        
        请求方式：GET /api/WorkflowTaskLogModelViewSet/by-process/
        
        请求参数：
            process_id: 流程ID
            
        返回结果：
        {
            "code": 2000,
            "data": [
                {
                    "id": "...",
                    "process_id": "...",
                    "node_name": "...",
                    "creator_name": "...",
                    "operation_name": "同意",
                    "des": "审批意见",
                    "create_datetime": "2025-01-14 10:00:00",
                    ...
                }
            ],
            "msg": "获取成功"
        }
        """
        process_id = request.query_params.get('process_id', None)
        if not process_id:
            return ErrorResponse(msg="process_id 参数必填")
        
        queryset = self.get_queryset().filter(process_id=process_id).order_by('create_datetime')
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")
    
    @action(methods=['GET'], detail=False, url_path='by-task')
    def get_by_task(self, request):
        """
        根据任务ID获取日志列表
        
        请求方式：GET /api/WorkflowTaskLogModelViewSet/by-task/
        
        请求参数：
            task_id: 任务ID
            
        返回结果：
        {
            "code": 2000,
            "data": [...],
            "msg": "获取成功"
        }
        """
        task_id = request.query_params.get('task_id', None)
        if not task_id:
            return ErrorResponse(msg="task_id 参数必填")
        
        queryset = self.get_queryset().filter(task_id=task_id).order_by('create_datetime')
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")
