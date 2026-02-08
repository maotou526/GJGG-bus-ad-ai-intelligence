'''
Description: 公司视图
Version: 1.0
Autor: 王晨
Date: 2025-10-09 17:32:55
LastEditors: 王晨
LastEditTime: 2025-12-01 15:38:21
'''
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import CompanyModel
from .serializers import (
    CompanyModelSerializer,
    CompanyModelCreateSerializer,
    CompanyModelUpdateSerializer,
    CompanyModelListSerializer,
    CompanyModelImportSerializer
)
from dvadmin.utils.field_permission import FieldPermissionMixin
from rest_framework.permissions import IsAuthenticated


class CompanyModelViewSet(CustomModelViewSet, FieldPermissionMixin):
    """
    公司管理视图集
    
    功能说明：
    - 提供公司的增删改查功能（使用DRF标准接口）
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作
    
    标准DRF接口：
    c
    - GET /api/CompanyModelViewSet/{id}/ - 获取单个公司详情
    - POST /api/CompanyModelViewSet/ - 创建公司
    - PUT /api/CompanyModelViewSet/{id}/ - 更新公司
    - DELETE /api/CompanyModelViewSet/{id}/ - 删除公司
    
    自定义接口：
    - POST /api/CompanyModelViewSet/delete_company/ - 批量删除公司（软删除）
    - POST /api/CompanyModelViewSet/enable_company/ - 启用/禁用公司
    """
    permission_classes = [IsAuthenticated]
    # 查询集
    queryset = CompanyModel.objects.all()

    # 默认序列化器（用于查询详情）
    serializer_class = CompanyModelSerializer

    # 列表序列化器（用于列表展示）
    list_serializer_class = CompanyModelListSerializer

    # 创建序列化器
    create_serializer_class = CompanyModelCreateSerializer

    # 更新序列化器
    update_serializer_class = CompanyModelUpdateSerializer

    # 导入序列化器
    import_serializer_class = CompanyModelImportSerializer

    # 导入字段配置
    import_field_dict = {
        'fullname': '公司全称',
        'shortname': '公司简称',
        'encode': '编码',
        'category': {
            'title': '公司分类',
            'choices': {
                'data': {
                    '1': 1,
                    '2': 2,
                }
            }
        },
        'sortcode': '排序码',
        'nature': '公司性质',
        'outerPhone': '外线电话',
        'email': '邮箱',
        'manager': '负责人',
        'address': '详细地址',
        'enabled_mark': {
            'title': '公司状态',
            'choices': {
                'data': {
                    '禁用': 0,
                    '启用': 1,
                    '正常': 1,
                }
            }
        },
    }

    # 过滤字段（支持精确查询）
    filter_fields = [
        'id', 'encode', 'shortname', 'fullname', 'category',
        'parentid', 'nature', 'enabled_mark', 'delete_mark'
    ]

    # 搜索字段（支持模糊查询）
    search_fields = ['fullname', 'shortname', 'encode', 'manager']

    # 排序字段
    ordering_fields = ['sortcode', 'fullname', 'create_datetime', 'update_datetime']

    # 默认排序
    ordering = ['sortcode', 'fullname']

    def list(self, request, *args, **kwargs):
        """
        列表查询（树形懒加载）：
        - 传入 parentid：仅返回该父节点下的数据
        - 未传 parentid：返回根节点（parentid is null）
        - 始终按启用且未删除过滤
        - 支持模糊搜索（search 参数：shortname / fullname / encode / manager）
        注：不做分页，前端树表自行控制懒加载
        """
        request.query_params._mutable = True
        params = request.query_params

        # 去除分页参数，避免影响树结构一次性返回
        page = params.get('page', None)
        limit = params.get('limit', None)
        if page is not None:
            del params['page']
        if limit is not None:
            del params['limit']

        parentid = params.get('parentid', None)
        base_filter = dict(delete_mark=0, enabled_mark=1)
        search = params.get('search', None)

        # 如果有搜索参数，忽略 parentid 限制，在所有公司中搜索
        if search and self.search_fields:
            from django.db.models import Q
            # 先应用基础过滤（启用且未删除）
            queryset = self.queryset.filter(**base_filter)
            # 构建搜索条件
            search_q = Q()
            for field in self.search_fields:
                search_q |= Q(**{f'{field}__icontains': search})
            queryset = queryset.filter(search_q)
        else:
            # 没有搜索参数时，按 parentid 过滤（树形懒加载）
            if params and parentid is not None and parentid != "":
                queryset = self.queryset.filter(parentid=parentid, **base_filter)
            else:
                queryset = self.queryset.filter(parentid__isnull=True, **base_filter)

        # 应用通用过滤（排除 search 参数，避免重复处理）
        if search:
            params._mutable = True
            params.pop('search', None)
        queryset = self.filter_queryset(queryset)

        serializer = self.get_serializer(queryset, many=True, request=request)
        return SuccessResponse(data=serializer.data, msg="获取成功")

    @action(methods=["GET"], detail=False, url_path="all_company",extra_filter_class=[])
    def all_company(self, request, *args, **kwargs):
        """
        获取所有公司（用于下拉框、树形组件等）
        
        请求方式：GET /api/CompanyModelViewSet/all_company/
        
        返回结果：
        {
            "code": 2000,
            "msg": "获取成功",
            "data": [
                {
                    "id": 1,
                    "shortname": "公司简称",
                    "parentid": null
                },
                ...
            ]
        }
        """
        queryset = self.filter_queryset(self.get_queryset())
        data = queryset.filter(delete_mark=0, enabled_mark=1).order_by('sortcode').values('shortname', 'id', 'parentid')
        return DetailResponse(data=data, msg="获取成功")

    @action(methods=['POST'], detail=False, url_path='delete_company')
    def delete_company(self, request):
        """
        删除公司（软删除）
        
        请求方式：POST /api/company/delete_company/
        
        请求参数：
        {
            "id": 1
        }
        或批量删除：
        {
            "ids": [1, 2, 3]
        }
        
        返回结果：
        {
            "code": 2000,
            "msg": "删除成功"
        }
        """
        # 获取公司ID
        company_id = request.data.get('id')
        company_ids = request.data.get('ids', [])

        if company_id:
            company_ids = [company_id]

        if not company_ids:
            return ErrorResponse(msg="缺少参数id或ids")

        # 批量软删除
        deleted_count = self.queryset.filter(id__in=company_ids).update(delete_mark=1)

        if deleted_count == 0:
            return ErrorResponse(msg="未找到要删除的公司")

        return SuccessResponse(msg=f"成功删除{deleted_count}家公司")

    @action(methods=['POST'], detail=False, url_path='enable_company')
    def enable_company(self, request):
        """
        启用/禁用公司
        
        请求方式：POST /api/company/enable_company/
        
        请求参数：
        {
            "id": 1,
            "enabled_mark": 1  // 1启用，0禁用
        }
        
        返回结果：
        {
            "code": 2000,
            "msg": "操作成功"
        }
        """
        # 获取参数
        company_id = request.data.get('id')
        enabled_mark = request.data.get('enabled_mark')

        if not company_id or enabled_mark is None:
            return ErrorResponse(msg="缺少参数id或enabled_mark")

        if enabled_mark not in [0, 1]:
            return ErrorResponse(msg="enabled_mark只能是0或1")

        # 更新状态
        try:
            # 使用 update() 方法直接更新数据库，避免触发模型验证
            updated_count = self.queryset.filter(id=company_id).update(enabled_mark=enabled_mark)

            if updated_count == 0:
                return ErrorResponse(msg="公司不存在")

            msg = "公司已启用" if enabled_mark == 1 else "公司已禁用"
            return SuccessResponse(msg=msg)
        except Exception as e:
            return ErrorResponse(msg=f"操作失败: {str(e)}")

    @action(methods=['GET'], detail=False, url_path='get_company_options')
    def get_company_options(self, request):
        """
        获取公司选项列表（用于下拉框）
        
        请求方式：GET /api/CompanyModelViewSet/get_company_options/
        
        请求参数：
        {
            "enabled_only": true  // 可选，是否只返回启用的公司，默认true
        }
        
        返回结果：
        {
            "code": 2000,
            "msg": "获取成功",
            "data": [
                {
                    "id": 1,
                    "fullName": "XX公司",
                    "shortname": "简称",
                    "enCode": "001"
                },
                ...
            ]
        }
        """
        # 获取参数，默认只返回启用的公司
        enabled_only = request.query_params.get('enabled_only', 'true').lower() == 'true'

        # 构建查询条件
        queryset = self.queryset.filter(delete_mark=0)  # 排除已删除的

        if enabled_only:
            queryset = queryset.filter(enabled_mark=1)  # 只返回启用的公司

        # 查询公司数据，只选择需要的字段
        companies = queryset.values('id', 'fullname', 'shortname', 'encode').order_by('sortcode', 'fullname')

        # 格式化返回数据
        data = [
            {
                'id': company['id'],
                'fullname': company['fullname'] or '',
                'shortname': company['shortname'] or '',
                'encode': company['encode'] or ''
            }
            for company in companies
        ]

        return SuccessResponse(data=data, msg=f"获取成功，共{len(data)}家公司")
