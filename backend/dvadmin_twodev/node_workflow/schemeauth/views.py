'''
Description: 流程模板权限视图
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework.decorators import action
from django.db import transaction
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import WorkflowSchemeAuthModel
from .serializers import (
    WorkflowSchemeAuthModelSerializer,
    WorkflowSchemeAuthModelCreateSerializer,
    WorkflowSchemeAuthModelUpdateSerializer,
    WorkflowSchemeAuthModelListSerializer,
    WorkflowSchemeAuthModelImportSerializer,
)


class WorkflowSchemeAuthModelViewSet(CustomModelViewSet):
    """
    流程模板权限管理视图集
    提供标准的 CRUD 接口和自定义业务接口
    """
    
    queryset = WorkflowSchemeAuthModel.objects.all()
    serializer_class = WorkflowSchemeAuthModelSerializer
    create_serializer_class = WorkflowSchemeAuthModelCreateSerializer
    update_serializer_class = WorkflowSchemeAuthModelUpdateSerializer
    list_serializer_class = WorkflowSchemeAuthModelListSerializer
    import_serializer_class = WorkflowSchemeAuthModelImportSerializer
    
    # 排序配置
    ordering_fields = ['scheme_info_id', 'obj_type', 'create_datetime', 'update_datetime']
    ordering = ['-create_datetime']
    
    # 搜索字段
    search_fields = ['scheme_info_id', 'obj_name']
    
    # 过滤字段
    filter_fields = ['id', 'scheme_info_id', 'obj_type', 'obj_id']
    
    @action(methods=['GET'], detail=False, url_path='by-scheme-info')
    def get_by_scheme_info(self, request):
        """
        根据流程信息ID获取权限列表
        
        请求方式：GET /api/WorkflowSchemeAuthModelViewSet/by-scheme-info/
        
        请求参数：
            scheme_info_id: 流程信息ID
            
        返回结果：
        {
            "code": 2000,
            "data": [
                {
                    "id": "...",
                    "scheme_info_id": "...",
                    "obj_type": 1,
                    "obj_type_display": "岗位",
                    ...
                }
            ],
            "msg": "获取成功"
        }
        """
        scheme_info_id = request.query_params.get('scheme_info_id', None)
        if not scheme_info_id:
            return ErrorResponse(msg="scheme_info_id 参数必填")
        
        queryset = self.get_queryset().filter(scheme_info_id=scheme_info_id)
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data, msg="获取成功")
    
    @action(methods=['POST'], detail=False, url_path='batch-save')
    def batch_save(self, request):
        """
        批量保存流程模板权限
        
        请求方式：POST /api/WorkflowSchemeAuthModelViewSet/batch-save/
        
        请求参数：
        {
            "scheme_info_id": "...",
            "auth_list": [
                {
                    "obj_type": 1,
                    "obj_id": "...",
                    "obj_name": "..."
                },
                ...
            ]
        }
        
        返回结果：
        {
            "code": 2000,
            "data": {
                "deleted_count": 2,
                "created_count": 3
            },
            "msg": "批量保存成功"
        }
        """
        scheme_info_id = request.data.get('scheme_info_id', None)
        auth_list = request.data.get('auth_list', [])
        
        if not scheme_info_id:
            return ErrorResponse(msg="scheme_info_id 参数必填")
        
        try:
            with transaction.atomic():
                # 删除该流程模板的所有权限记录
                deleted_count = WorkflowSchemeAuthModel.objects.filter(
                    scheme_info_id=scheme_info_id
                ).delete()[0]
                
                # 批量创建新权限记录
                auth_objects = []
                for auth_data in auth_list:
                    auth_obj = WorkflowSchemeAuthModel(
                        scheme_info_id=scheme_info_id,
                        obj_type=auth_data.get('obj_type'),
                        obj_id=auth_data.get('obj_id'),
                        obj_name=auth_data.get('obj_name'),
                    )
                    auth_objects.append(auth_obj)
                
                WorkflowSchemeAuthModel.objects.bulk_create(auth_objects)
                created_count = len(auth_objects)
                
                return SuccessResponse(
                    data={
                        "deleted_count": deleted_count,
                        "created_count": created_count
                    },
                    msg="批量保存成功"
                )
        except Exception as e:
            return ErrorResponse(msg=f"批量保存失败: {str(e)}")
