'''
Description: 流程任务视图
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework.decorators import action
from django.db.models import Q
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import WorkflowTaskModel
from .serializers import (
    WorkflowTaskModelSerializer,
    WorkflowTaskModelCreateSerializer,
    WorkflowTaskModelUpdateSerializer,
    WorkflowTaskModelListSerializer,
    WorkflowTaskModelImportSerializer,
)


class WorkflowTaskModelViewSet(CustomModelViewSet):
    """
    流程任务管理视图集
    提供标准的 CRUD 接口和自定义业务接口
    """
    
    queryset = WorkflowTaskModel.objects.all()
    serializer_class = WorkflowTaskModelSerializer
    create_serializer_class = WorkflowTaskModelCreateSerializer
    update_serializer_class = WorkflowTaskModelUpdateSerializer
    list_serializer_class = WorkflowTaskModelListSerializer
    import_serializer_class = WorkflowTaskModelImportSerializer
    
    # 排序配置
    ordering_fields = ['process_id', 'node_id', 'type', 'is_finished', 'create_datetime', 'update_datetime']
    ordering = ['-create_datetime']
    
    # 搜索字段
    search_fields = ['process_id', 'node_id', 'node_name']
    
    # 过滤字段
    filter_fields = ['id', 'process_id', 'node_id', 'type', 'is_finished', 'is_batch_audit']
    
    @action(methods=['GET'], detail=False, url_path='my-todo')
    def get_my_todo(self, request):
        """
        获取我的待办任务

        请求方式：GET /api/WorkflowTaskModelViewSet/my-todo/
        """
        from dvadmin_twodev.node_workflow.task.services import WorkflowTaskService

        keyword = request.query_params.get('keyword', '')
        scheme_code = request.query_params.get('schemeCode', '')
        start_time = request.query_params.get('StartTime', '')
        end_time = request.query_params.get('EndTime', '')
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))

        try:
            result = WorkflowTaskService.get_my_tasks(
                user=request.user,
                keyword=keyword,
                scheme_code=scheme_code,
                start_time=start_time,
                end_time=end_time,
                page=page,
                limit=limit
            )
            return SuccessResponse(data=result, msg="获取成功")
        except Exception as e:
            return ErrorResponse(msg=f"获取失败: {str(e)}")
    
    @action(methods=['GET'], detail=False, url_path='my-done')
    def get_my_done(self, request):
        """
        获取我的已办任务

        请求方式：GET /api/WorkflowTaskModelViewSet/my-done/
        """
        from dvadmin_twodev.node_workflow.task.services import WorkflowTaskService

        keyword = request.query_params.get('keyword', '')
        scheme_code = request.query_params.get('schemeCode', '')
        start_time = request.query_params.get('StartTime', '')
        end_time = request.query_params.get('EndTime', '')
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))

        try:
            result = WorkflowTaskService.get_finished_tasks(
                user=request.user,
                keyword=keyword,
                scheme_code=scheme_code,
                start_time=start_time,
                end_time=end_time,
                page=page,
                limit=limit
            )
            return SuccessResponse(data=result, msg="获取成功")
        except Exception as e:
            return ErrorResponse(msg=f"获取失败: {str(e)}")

    @action(methods=['GET'], detail=False, url_path='my-create')
    def get_my_create(self, request):
        """
        获取我发起的流程

        请求方式：GET /api/WorkflowTaskModelViewSet/my-create/
        """
        from dvadmin_twodev.node_workflow.task.services import WorkflowTaskService

        keyword = request.query_params.get('keyword', '')
        scheme_code = request.query_params.get('schemeCode', '')
        start_time = request.query_params.get('StartTime', '')
        end_time = request.query_params.get('EndTime', '')
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 20))

        try:
            result = WorkflowTaskService.get_my_create_tasks(
                user=request.user,
                keyword=keyword,
                scheme_code=scheme_code,
                start_time=start_time,
                end_time=end_time,
                page=page,
                limit=limit
            )
            return SuccessResponse(data=result, msg="获取成功")
        except Exception as e:
            return ErrorResponse(msg=f"获取失败: {str(e)}")
    
    @action(methods=['GET'], detail=False, url_path='by-process')
    def get_by_process(self, request):
        """
        根据流程ID获取任务列表
        """
        process_id = request.query_params.get('process_id', None)
        if not process_id:
            return ErrorResponse(msg="process_id 参数必填")
        
        queryset = self.get_queryset().filter(process_id=process_id)
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")
