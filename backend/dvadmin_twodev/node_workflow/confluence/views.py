'''
Description: 会签视图
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework.decorators import action
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import WorkflowConfluenceModel
from .serializers import (
    WorkflowConfluenceModelSerializer,
    WorkflowConfluenceModelCreateSerializer,
    WorkflowConfluenceModelUpdateSerializer,
    WorkflowConfluenceModelListSerializer,
    WorkflowConfluenceModelImportSerializer,
)


class WorkflowConfluenceModelViewSet(CustomModelViewSet):
    """
    会签管理视图集
    提供标准的 CRUD 接口和自定义业务接口
    """
    
    queryset = WorkflowConfluenceModel.objects.all()
    serializer_class = WorkflowConfluenceModelSerializer
    create_serializer_class = WorkflowConfluenceModelCreateSerializer
    update_serializer_class = WorkflowConfluenceModelUpdateSerializer
    list_serializer_class = WorkflowConfluenceModelListSerializer
    import_serializer_class = WorkflowConfluenceModelImportSerializer
    
    # 排序配置
    ordering_fields = ['process_id', 'node_id', 'state', 'create_datetime', 'update_datetime']
    ordering = ['-create_datetime']
    
    # 搜索字段
    search_fields = ['process_id', 'node_id']
    
    # 过滤字段
    filter_fields = ['id', 'process_id', 'node_id', 'form_node_id', 'state']
    
    @action(methods=['GET'], detail=False, url_path='by-process-node')
    def get_by_process_node(self, request):
        """
        根据流程ID和节点ID获取会签记录
        
        请求方式：GET /api/WorkflowConfluenceModelViewSet/by-process-node/
        
        请求参数：
            process_id: 流程ID
            node_id: 节点ID
            
        返回结果：
        {
            "code": 2000,
            "data": [
                {
                    "id": "...",
                    "process_id": "...",
                    "node_id": "...",
                    "state": 1,
                    "state_display": "同意",
                    ...
                }
            ],
            "msg": "获取成功"
        }
        """
        process_id = request.query_params.get('process_id', None)
        node_id = request.query_params.get('node_id', None)
        
        if not process_id or not node_id:
            return ErrorResponse(msg="process_id 和 node_id 参数必填")
        
        queryset = self.get_queryset().filter(
            process_id=process_id,
            node_id=node_id
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")
    
    @action(methods=['GET'], detail=False, url_path='progress')
    def get_progress(self, request):
        """
        获取会签进度统计
        
        请求方式：GET /api/WorkflowConfluenceModelViewSet/progress/
        
        请求参数：
            process_id: 流程ID
            node_id: 节点ID
            
        返回结果：
        {
            "code": 2000,
            "data": {
                "total": 3,
                "agreed": 2,
                "disagreed": 0,
                "pending": 1
            },
            "msg": "获取成功"
        }
        """
        process_id = request.query_params.get('process_id', None)
        node_id = request.query_params.get('node_id', None)
        
        if not process_id or not node_id:
            return ErrorResponse(msg="process_id 和 node_id 参数必填")
        
        queryset = self.get_queryset().filter(
            process_id=process_id,
            node_id=node_id
        )
        
        total = queryset.count()
        agreed = queryset.filter(state=1).count()
        disagreed = queryset.filter(state=0).count()
        pending = total - agreed - disagreed
        
        return SuccessResponse(
            data={
                "total": total,
                "agreed": agreed,
                "disagreed": disagreed,
                "pending": pending
            },
            msg="获取成功"
        )
