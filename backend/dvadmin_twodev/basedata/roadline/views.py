'''
Description: 线路视图
Version: 1.0
Autor: 王晨
Date: 2025-10-09 17:32:55
LastEditors: 王晨
LastEditTime: 2025-12-30 13:56:00
'''
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import RoadlineModel
from .serializers import (
    RoadlineModelSerializer,
    RoadlineModelCreateSerializer,
    RoadlineModelUpdateSerializer,
    RoadlineModelListSerializer,
    RoadlineModelImportSerializer,
    RoadlineModelSimpleSerializer
)
from dvadmin.utils.field_permission import FieldPermissionMixin
from rest_framework.permissions import IsAuthenticated


class RoadlineModelViewSet(CustomModelViewSet, FieldPermissionMixin):
    """
    线路管理视图集
    
    功能说明：
    - 提供线路的增删改查功能（使用DRF标准接口）
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作
    
    标准DRF接口：
    - GET /api/RoadlineModelViewSet/ - 获取线路列表
    - GET /api/RoadlineModelViewSet/{id}/ - 获取单个线路详情
    - POST /api/RoadlineModelViewSet/ - 创建线路
    - PUT /api/RoadlineModelViewSet/{id}/ - 更新线路
    - DELETE /api/RoadlineModelViewSet/{id}/ - 删除线路
    
    自定义接口：
    - POST /api/RoadlineModelViewSet/delete_roadline/ - 批量删除线路（软删除）
    - POST /api/RoadlineModelViewSet/enable_roadline/ - 启用/禁用线路
    """
    # 查询集
    queryset = RoadlineModel.objects.all()

    # 默认序列化器（用于查询详情）
    serializer_class = RoadlineModelSerializer

    # 列表序列化器（用于列表展示）
    list_serializer_class = RoadlineModelListSerializer

    # 创建序列化器
    create_serializer_class = RoadlineModelCreateSerializer

    # 更新序列化器
    update_serializer_class = RoadlineModelUpdateSerializer

    # 导入序列化器
    import_serializer_class = RoadlineModelImportSerializer

    # 导出序列化器
    export_serializer_class = RoadlineModelListSerializer

    # 导出字段配置
    export_field_label = {
        'id': 'ID',
        'line_name': '线路名称',
        'company_code': '公司编码',
        'company_name': '公司名称',
        'branch': '车队',
        'normal_code': '企业线路编码',
        'ygc_code': '行业线路编号',
        'line_length': '线路长度（公里）',
        'non_linear_coefficient': '非直线系数',
        'line_type': '线路类型',
        'sell_type': '售票方式',
        'ticket_price_type': '票价类型',
        'ticket_price': '票价（元）',
        'yy_type': '运营时段分类',
        'listing_type': '挂牌类型',
        'schedule_type': '定班类型',
        'exec_day': '启用日期',
        'expiry_day': '截止日期',
        'enabled_mark': '启用状态',
        'delete_mark': '删除状态',
        'description': '描述',
        'create_datetime': '创建时间',
        'update_datetime': '更新时间',
    }

    # 导入字段配置（与列表展示字段保持一致）
    import_field_dict = {
        'company_name': '公司名称',
        'branch': '车队',
        'line_name': '线路名称',
        'normal_code': '企业线路编码',
        'ygc_code': '行业线路编号',
        'line_length': '线路长度（公里）',
        'line_type': {
            'title': '线路类型',
            'choices': {
                'data': {
                    '普通': 0,
                    '挂牌线': 1,
                    '区间': 2,
                    '同名区间': 3,
                    '定班线': 4,
                    '定制公交': 5,
                    '高峰线': 6,
                    '夜宵线': 7,
                    '低谷定班线': 8,
                }
            }
        },
        'sell_type': {
            'title': '售票方式',
            'choices': {
                'data': {
                    '无人售票': 1,
                    '有人售票': 2,
                }
            }
        },
        'ticket_price_type': {
            'title': '票价类型',
            'choices': {
                'data': {
                    '单一票价': 1,
                    '多级票价': 2,
                }
            }
        },
        'ticket_price': '票价（元）',
        'yy_type': {
            'title': '运营时段分类',
            'choices': {
                'data': {
                    '全日线': 1,
                    '高峰线': 2,
                    '夜宵线': 3,
                }
            }
        },
        'listing_type': {
            'title': '挂牌类型',
            'choices': {
                'data': {
                    '无挂牌': 1,
                    '全日挂牌': 2,
                    '高峰挂牌': 3,
                }
            }
        },
        'schedule_type': {
            'title': '定班类型',
            'choices': {
                'data': {
                    '无定班': 1,
                    '定班线': 2,
                }
            }
        },
        'enabled_mark': {
            'title': '启用状态',
            'choices': {
                'data': {
                    '禁用': 0,
                    '启用': 1,
                }
            }
        },
        'bus_count': '配车数',
        'ad_bus_count': '广告车辆数',
        'exec_day': '启用日期',
        'expiry_day': '截止日期',
        'description': '描述',
    }

    # 过滤字段（支持精确查询）
    filter_fields = [
        "id",
        "company_belong_id",
        "company_code",
        "company_name",
        "branch",
        "normal_code",
        "ygc_code",
        "line_name",
        "line_type",
        "sell_type",
        "ticket_price_type",
        "yy_type",
        "listing_type",
        "schedule_type",
        "enabled_mark",
        "delete_mark",
    ]

    # 搜索字段（支持模糊查询）
    search_fields = ['line_name', 'company_name', 'normal_code', 'ygc_code']

    # 排序字段（支持前端表格排序）
    ordering_fields = [
        'id',                   # 线路ID
        'line_name',            # 线路名称
        'company_code',         # 公司编码
        'company_name',         # 公司名
        'branch',               # 车队
        'normal_code',          # 企业线路编码
        'ygc_code',            # 行业线路编号
        'line_length',          # 线路长度
        'non_linear_coefficient',  # 非直线系数
        'line_type',            # 线路类型
        'sell_type',            # 售票方式
        'ticket_price_type',    # 票价类型
        'ticket_price',         # 票价
        'yy_type',             # 运营时段分类
        'listing_type',         # 挂牌类型
        'schedule_type',        # 定班类型
        'exec_day',            # 启用日期
        'expiry_day',          # 截止日期
        'enabled_mark',         # 启用标记
        'delete_mark',          # 删除标记
        'create_datetime',      # 创建时间
        'update_datetime',      # 修改时间
    ]

    # 默认排序
    ordering = ['line_name']
    
    @action(methods=['GET'], detail=False, url_path='get_all', permission_classes=[IsAuthenticated])
    def get_all(self, request):
        """
        获取全量数据（支持多种过滤器）
        
        功能说明：
        1. 支持通过 fields 参数控制返回的字段类型（simple/list/full）
        2. 支持通过 date 或 month 参数过滤有效时间范围内的数据（需用户传递日期参数）
        3. 支持所有现有的过滤字段（filter_fields）和搜索字段（search_fields）
        4. 返回全量数据，不分页
        
        请求参数：
        - fields: 可选，控制返回字段类型
          * simple: 只返回 id、线路名称、公司名称、线路编码
          * list: 返回列表序列化器的字段（优化后的字段列表）
          * full: 返回全部字段（默认）
        - date: 可选，指定查询日期（格式：YYYY-MM-DD），用于过滤有效时间范围
          如果传递此参数，则只返回 exec_day <= date <= expiry_day 的有效数据
          如果不传递此参数，则不进行时间范围过滤，返回所有数据
        - month: 可选，指定查询月份（格式：YYYY-MM），使用该月最后一天作为查询日期
          如果传递此参数，则只返回该月最后一天有效的所有数据
          优先级高于 date 参数（如果 month 和 date 都传递，优先使用 month）
          如果不传递此参数，则不进行时间范围过滤，返回所有数据
        - 其他过滤参数：支持所有 filter_fields 中定义的字段进行过滤
          * 例如：company_name=太仓公交、line_type=1、enabled_mark=1 等
        
        请求示例：
        GET /api/RoadlineModelViewSet/get_all/?fields=simple
        GET /api/RoadlineModelViewSet/get_all/?fields=list&date=2025-12-15
        GET /api/RoadlineModelViewSet/get_all/?fields=full&month=2025-12
        GET /api/RoadlineModelViewSet/get_all/?fields=simple&company_name=太仓公交&enabled_mark=1
        GET /api/RoadlineModelViewSet/get_all/?date=2025-12-15&line_type=1
        
        返回结果：
        {
            "code": 2000,
            "msg": "获取成功，共 100 条数据",
            "data": [...]
        }
        """
        try:
            # 获取字段类型参数
            fields_type = request.query_params.get('fields', 'full').lower()
            
            # 根据参数选择序列化器
            if fields_type == 'simple':
                serializer_class = RoadlineModelSimpleSerializer
            elif fields_type == 'list':
                serializer_class = RoadlineModelListSerializer
            else:  # full 或其他
                serializer_class = RoadlineModelSerializer
            
            # 获取基础查询集并应用所有过滤条件（filter_fields 和 search_fields）
            queryset = self.filter_queryset(super().get_queryset())
            
            # 应用时间范围过滤（不传 default_date，表示没有参数时不进行过滤）
            # 只有用户传递了 date 或 month 参数时，才会进行有效时间范围过滤
            queryset, error_response = self._apply_valid_period_filter(request, queryset)
            if error_response:
                return error_response
            
            # 序列化数据
            serializer = serializer_class(queryset, many=True, request=request)
            
            return DetailResponse(
                data=serializer.data,
                msg=f"获取成功，共 {len(serializer.data)} 条数据"
            )
        
        except Exception as e:
            return ErrorResponse(msg=f"获取数据失败: {str(e)}")

    @action(
        methods=["GET"],
        detail=False,
        url_path="get_line_options",
        permission_classes=[IsAuthenticated],
    )
    def get_line_options(self, request):
        """
        获取线路选项列表（用于下拉框）
        
        请求方式：GET /api/RoadlineModelViewSet/get_line_options/
        
        请求参数：
        {
            "enabled_only": true  // 可选，是否只返回启用的线路，默认true
        }
        
        返回结果：
        {
            "code": 2000,
            "msg": "获取成功",
            "data": [
                {
                    "id": 1,
                    "line_name": "1路",
                    "line_code": "001",
                    "company_name": "公交公司"
                },
                ...
            ]
        }
        """
        # 获取参数，默认只返回启用的线路
        enabled_only = request.query_params.get('enabled_only', 'true').lower() == 'true'

        # 构建查询条件
        queryset = self.queryset.filter(delete_mark=0)  # 排除已删除的

        if enabled_only:
            queryset = queryset.filter(enabled_mark=1)  # 只返回启用的线路

        # 查询线路数据，只选择需要的字段
        lines = queryset.values('id', 'line_name', 'normal_code', 'company_name').order_by('line_name')

        # 格式化返回数据
        data = [
            {
                'id': line['id'],
                'line_name': line['line_name'],
                'line_code': line['normal_code'] or '',
                'company_name': line['company_name'] or ''
            }
            for line in lines
        ]

        return SuccessResponse(data=data, msg=f"获取成功，共{len(data)}条线路")

    @action(
        methods=["GET"],
        detail=False,
        url_path="network_mileage_stats",
        permission_classes=[IsAuthenticated],
    )
    def network_mileage_stats(self, request):
        """
        线网里程统计
        
        功能说明：
        1. 统计所有线路的总里程（基于主表 line_length 字段）
        2. 每条线路只统计一次，不考虑上下行
        3. 支持按公司筛选和启用状态过滤
        
        请求方式：GET /api/RoadlineModelViewSet/network_mileage_stats/
        
        查询参数：
        - company_name: 可选，按公司名称过滤
        - enabled_only: 可选，是否只统计启用的线路，默认true
        
        返回结果：
        {
            "code": 2000,
            "data": {
                "total_mileage": 1177.45,      // 总线网里程（公里）
                "line_count": 56,               // 线路总数
                "avg_line_mileage": 21.03       // 平均每条线路里程
            },
            "msg": "统计成功！总线网里程 1177.45 公里"
        }
        """
        
        try:
            # 获取查询参数
            company_name = request.query_params.get('company_name', None)
            enabled_only = request.query_params.get('enabled_only', 'true').lower() == 'true'

            # 构建查询条件
            lines_query = self.queryset.filter(
                Q(delete_mark=0) | Q(delete_mark__isnull=True)
            )

            if enabled_only:
                lines_query = lines_query.exclude(enabled_mark=0)

            if company_name:
                lines_query = lines_query.filter(company_name__icontains=company_name)

            # 统计数据
            stats = lines_query.aggregate(
                total_mileage=Sum('line_length'),
                line_count=Count('id'),
                avg_mileage=Avg('line_length')
            )

            total_mileage = float(stats['total_mileage'] or 0)
            line_count = stats['line_count'] or 0
            avg_mileage = float(stats['avg_mileage'] or 0)

            result = {
                'total_mileage': round(total_mileage, 2),
                'line_count': line_count,
                'avg_line_mileage': round(avg_mileage, 2)
            }

            return SuccessResponse(
                data=result,
                msg=f"统计成功！总线网里程 {result['total_mileage']} 公里"
            )

        except Exception as e:
            return ErrorResponse(msg=f"统计失败: {str(e)}")

    @action(
        methods=["GET"],
        detail=False,
        url_path="count",
        permission_classes=[IsAuthenticated],
    )
    def count(self, request):
        """
        统计线路数量
        
        功能说明：
        1. 支持所有 filter_fields 中定义的字段进行过滤
        2. 支持 search_fields 中定义的字段进行模糊搜索
        3. 支持 date 和 month 参数进行时间范围过滤
        4. 返回符合条件的线路总数
        
        请求方式：GET /api/RoadlineModelViewSet/count/
        
        查询参数：
        - 支持所有 filter_fields 中的字段：id、company_name、line_name、line_type、enabled_mark 等
        - 支持 search_fields 中的字段进行模糊搜索：line_name、company_name、normal_code、ygc_code
        - date: 可选，指定查询日期（格式：YYYY-MM-DD），用于过滤有效时间范围
        - month: 可选，指定查询月份（格式：YYYY-MM），使用该月最后一天作为查询日期
        
        请求示例：
        GET /api/RoadlineModelViewSet/count/
        GET /api/RoadlineModelViewSet/count/?company_name=太仓公交
        GET /api/RoadlineModelViewSet/count/?line_type=1&enabled_mark=1
        GET /api/RoadlineModelViewSet/count/?date=2025-12-15
        GET /api/RoadlineModelViewSet/count/?month=2025-12&line_type=1
        GET /api/RoadlineModelViewSet/count/?search=1路
        
        返回结果：
        {
            "code": 2000,
            "data": {
                "count": 45
            },
            "msg": "统计成功"
        }
        """
        try:
            # 获取基础查询集并应用所有过滤条件（类似 list 方法）
            queryset = self.filter_queryset(super().get_queryset())

            # 应用时间范围过滤（不传 default_date，表示没有参数时不进行过滤）
            queryset, error_response = self._apply_valid_period_filter(request, queryset)
            if error_response:
                return error_response

            # 统计数量
            count = queryset.count()

            return DetailResponse(
                data={'count': count},
                msg="统计成功"
            )

        except Exception as e:
            return ErrorResponse(msg=f"统计失败: {str(e)}")

