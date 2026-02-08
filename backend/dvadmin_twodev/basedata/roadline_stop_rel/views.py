"""
Description: 站点关联视图
Version: 1.0
Autor: 王晨
Date: 2025-10-14
LastEditors: 王晨
LastEditTime: 2025-12-12
"""
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, ErrorResponse
from .models import RoadlineStopRelModel
from .serializers import (
    RoadlineStopRelModelSerializer,
    RoadlineStopRelModelListSerializer,
    RoadlineStopRelSimpleSerializer,
    RoadlineStopRelImportSerializer
)
import logging

logger = logging.getLogger(__name__)


class RoadlineStopRelModelViewSet(CustomModelViewSet):
    """
    站点关联管理视图集
    提供标准CRUD接口和数据导入功能
    """
    queryset = RoadlineStopRelModel.objects.all()
    serializer_class = RoadlineStopRelModelSerializer
    list_serializer_class = RoadlineStopRelModelListSerializer
    
    def get_queryset(self):
        """
        自定义查询集
        优化查询性能，预加载关联对象，并过滤掉关联对象不存在的记录
        """
        from dvadmin_twodev.basedata.roadline.models import RoadlineModel
        from dvadmin_twodev.basedata.roadline_detail.models import RoadlineDetailModel
        from django.db.models import Q, Exists, OuterRef
        
        queryset = super().get_queryset()
        
        # 使用 select_related 预加载关联对象，提高查询性能
        # 注意：如果关联对象不存在，select_related 不会报错，但访问时会返回 None
        queryset = queryset.select_related('roadline_id', 'line_dtl_id')
        
        # 使用 EXISTS 子查询过滤掉关联对象不存在的记录（更高效）
        # 只返回 roadline_id 为 None 或对应的 RoadlineModel 存在且未删除的记录
        # 只返回 line_dtl_id 为 None 或对应的 RoadlineDetailModel 存在且未删除的记录
        roadline_exists = RoadlineModel.objects.filter(
            id=OuterRef('roadline_id'),
            delete_mark=0
        )
        line_dtl_exists = RoadlineDetailModel.objects.filter(
            id=OuterRef('line_dtl_id'),
            delete_mark=0
        )
        
        queryset = queryset.filter(
            Q(roadline_id__isnull=True) | Exists(roadline_exists),
            Q(line_dtl_id__isnull=True) | Exists(line_dtl_exists)
        )
        
        return queryset
    
    def get_serializer_context(self):
        """为序列化器添加上下文，包含站点信息缓存"""
        context = super().get_serializer_context()
        
        # 如果是列表查询，批量加载站点信息到缓存
        if self.action == 'list':
            queryset = self.filter_queryset(self.get_queryset())
            # 获取所有唯一的 stop_code
            stop_codes = set(
                queryset.exclude(stop_code__isnull=True)
                       .exclude(stop_code='')
                       .values_list('stop_code', flat=True)
                       .distinct()
            )
            
            if stop_codes:
                try:
                    from dvadmin_twodev.basedata.roadline_stop.models import RoadlineStopModel
                    stops = RoadlineStopModel.objects.filter(
                        stop_code__in=stop_codes,
                        delete_mark=0
                    )
                    # 构建缓存字典
                    stop_cache = {stop.stop_code: stop for stop in stops}
                    context['stop_cache'] = stop_cache
                except Exception:
                    context['stop_cache'] = {}
            else:
                context['stop_cache'] = {}
        
        return context
    
    # 导入序列化器
    import_serializer_class = RoadlineStopRelImportSerializer
    
    # 导入字段配置
    import_field_dict = {
        'line_name': '线路名称',
        'level_name': '站点名称',
        'level_id': '站序',
        'up_down': {
            'title': '线路方向',
            'choices': {
                'data': {
                    '上行': 0,
                    '下行': 1,
                }
            }
        },
        'lon02': '经度(GCJ02)',
        'lat02': '纬度(GCJ02)',
    }
    
    @action(
        methods=["GET"],
        detail=False,
        url_path="get_all",
        permission_classes=[IsAuthenticated],
    )
    def get_all(self, request):
        """
        获取全量数据
        
        功能说明：
        1. 支持通过 fields 参数控制返回的字段类型
        2. 返回全量数据，不分页
        
        请求参数：
        - fields: 可选，控制返回字段类型
          * simple: 只返回 id、线路名称、站点名称、站序
          * list: 返回列表序列化器的字段（优化后的字段列表）
          * full: 返回全部字段（默认）
        
        请求示例：
        GET /api/RoadlineStopRelModelViewSet/get_all/?fields=simple
        GET /api/RoadlineStopRelModelViewSet/get_all/?fields=list
        GET /api/RoadlineStopRelModelViewSet/get_all/?fields=full
        
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
                serializer_class = RoadlineStopRelSimpleSerializer
            elif fields_type == 'list':
                serializer_class = RoadlineStopRelModelListSerializer
            else:  # full 或其他
                serializer_class = RoadlineStopRelModelSerializer
            
            # 获取基础查询集（应用过滤条件）
            queryset = self.filter_queryset(self.get_queryset())
            
            # 按站序排序
            queryset = queryset.order_by('level_id')
            
            # 序列化数据
            serializer = serializer_class(queryset, many=True, request=request)
            
            return DetailResponse(
                data=serializer.data,
                msg=f"获取成功，共 {len(serializer.data)} 条数据"
            )
        
        except Exception as e:
            logger.error(f"[获取全量数据] 执行失败: {str(e)}", exc_info=True)
            return ErrorResponse(msg=f"获取数据失败: {str(e)}")