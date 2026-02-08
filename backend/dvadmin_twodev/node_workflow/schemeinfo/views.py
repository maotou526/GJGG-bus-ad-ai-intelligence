'''
Description: 流程模板信息视图
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework.decorators import action
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import WorkflowSchemeInfoModel
from .serializers import (
    WorkflowSchemeInfoModelSerializer,
    WorkflowSchemeInfoModelCreateSerializer,
    WorkflowSchemeInfoModelUpdateSerializer,
    WorkflowSchemeInfoModelListSerializer,
    WorkflowSchemeInfoModelImportSerializer,
)


class WorkflowSchemeInfoModelViewSet(CustomModelViewSet):
    """
    流程模板信息管理视图集
    提供标准的 CRUD 接口和自定义业务接口
    """

    queryset = WorkflowSchemeInfoModel.objects.all()
    serializer_class = WorkflowSchemeInfoModelSerializer
    create_serializer_class = WorkflowSchemeInfoModelCreateSerializer
    update_serializer_class = WorkflowSchemeInfoModelUpdateSerializer
    list_serializer_class = WorkflowSchemeInfoModelListSerializer
    import_serializer_class = WorkflowSchemeInfoModelImportSerializer

    # 排序配置
    ordering_fields = ['code', 'name', 'create_datetime', 'update_datetime']
    ordering = ['-create_datetime']

    # 搜索字段
    search_fields = ['code', 'name', 'category', 'description']

    # 过滤字段（~前缀表示模糊搜索 icontains）
    filter_fields = ['id', '~code', '~name', 'category', 'mark', 'is_in_app', 'enabled_mark']

    # 禁用 enabled_mark 默认过滤，列表需要显示所有状态的数据
    skip_enabled_mark_filter = True

    def list(self, request, *args, **kwargs):
        """
        重写 list 方法，按照原始力软逻辑返回数据
        查询 SchemeInfo 主表，关联 Scheme 获取额外字段（type, create_datetime, creator_name）
        """
        from dvadmin_twodev.node_workflow.scheme.models import WorkflowSchemeModel
        from django.db.models import OuterRef, Subquery
        
        # 获取基础查询集
        queryset = self.filter_queryset(self.get_queryset())
        
        # 子查询：获取关联的 scheme 信息
        scheme_subquery = WorkflowSchemeModel.objects.filter(
            id=OuterRef('scheme_id')
        ).values('type', 'create_datetime', 'creator_name')[:1]
        
        # 使用 annotate 添加关联字段
        queryset = queryset.annotate(
            type=Subquery(scheme_subquery.values('type')),
            scheme_create_datetime=Subquery(scheme_subquery.values('create_datetime')),
            scheme_creator_name=Subquery(scheme_subquery.values('creator_name'))
        )
        
        # 分页
        page = self.paginate_queryset(queryset)
        if page is not None:
            # 手动构造返回数据
            data = []
            for item in page:
                item_data = {
                    'id': str(item.id),
                    'code': item.code,
                    'name': item.name,
                    'category': item.category,
                    'scheme_id': item.scheme_id,
                    'enabled_mark': item.enabled_mark,
                    'mark': item.mark,
                    'is_in_app': item.is_in_app,
                    'description': item.description,
                    'create_datetime': item.create_datetime.strftime('%Y-%m-%d %H:%M:%S') if item.create_datetime else None,
                    'creator_name': item.creator_name,
                    # 来自关联的 scheme 表
                    'type': item.type if hasattr(item, 'type') else None,
                    'scheme_create_datetime': item.scheme_create_datetime.strftime('%Y-%m-%d %H:%M:%S') if hasattr(item, 'scheme_create_datetime') and item.scheme_create_datetime else None,
                    'scheme_creator_name': item.scheme_creator_name if hasattr(item, 'scheme_creator_name') else None,
                }
                data.append(item_data)
            
            return self.get_paginated_response(data)
        
        # 如果没有分页，直接返回所有数据
        serializer = self.get_serializer(queryset, many=True)
        return SuccessResponse(data=serializer.data)

