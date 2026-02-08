'''
Description: 媒体类型视图
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import SuccessResponse
from rest_framework.decorators import action
from .models import AdMediaTypeModel
from .serializers import AdMediaTypeModelSerializer
from dvadmin_twodev.basedata.media_type_composition.models import AdMediaTypeCompositionModel


class AdMediaTypeModelViewSet(CustomModelViewSet):
    """
    媒体类型管理视图集
    提供标准CRUD接口和树形结构支持
    """
    queryset = AdMediaTypeModel.objects.all()
    serializer_class = AdMediaTypeModelSerializer
    
    # 配置基本的过滤和搜索字段
    # 注意：is_composite 不在 filterset_fields 中，因为需要在 get_queryset 中手动处理字符串转布尔值
    filterset_fields = ['media_category', 'enabled_mark', 'delete_mark']
    search_fields = ['media_name']
    
    def get_queryset(self):
        """
        自定义查询集
        支持树形结构：根节点为组合类型，子节点为基础类型
        """
        queryset = super().get_queryset()

        # 统一过滤掉已删除的数据
        queryset = queryset.filter(delete_mark=0)

        # 处理 is_composite 参数（URL 参数是字符串，需要转换为布尔值）
        # 说明：
        # - 如果显式传入 is_composite=true/false，则按参数过滤
        # - 如果未传入 is_composite，则不过滤该字段，返回所有类型（组合 + 基础）
        is_composite_param = self.request.query_params.get('is_composite', None)
        if is_composite_param is not None:
            # 将字符串转换为布尔值
            if str(is_composite_param).lower() in ['true', '1', 't']:
                queryset = queryset.filter(is_composite=True)
            elif str(is_composite_param).lower() in ['false', '0', 'f']:
                queryset = queryset.filter(is_composite=False)
        
        # 如果传入了 composite_type_id，说明是懒加载子节点，返回该组合类型下的基础类型
        composite_type_id = self.request.query_params.get('composite_type_id', None)

        if composite_type_id:
            # 获取该组合类型包含的基础类型ID列表
            composition_list = AdMediaTypeCompositionModel.objects.filter(
                composite_type_id=composite_type_id,
                delete_mark=0
            ).values_list('component_type_id', flat=True)
            # 返回这些基础类型，按 sort_order 排序
            queryset = queryset.filter(id__in=composition_list, delete_mark=0)
            # 通过 composition 表获取 sort_order 并排序
            from django.db.models import Case, When, IntegerField
            sort_orders = {}
            for comp in AdMediaTypeCompositionModel.objects.filter(
                composite_type_id=composite_type_id,
                delete_mark=0
            ):
                # component_type_id 现在是字符串类型，直接使用
                sort_orders[comp.component_type_id] = comp.sort_order or 0
            
            if sort_orders:
                # 使用 Case/When 进行排序
                when_list = [When(id=type_id, then=sort_order) 
                           for type_id, sort_order in sort_orders.items()]
                queryset = queryset.annotate(
                    composition_sort_order=Case(*when_list, default=999, output_field=IntegerField())
                ).order_by('composition_sort_order', 'sort_order', 'media_name')
        else:
            # 默认排序：组合类型优先，其次按显示顺序和名称排序
            queryset = queryset.order_by('-is_composite', 'sort_order', 'media_name')

        return queryset
    
    def list(self, request, *args, **kwargs):
        """
        重写 list 方法，为组合类型添加 hasChild 字段
        支持树形结构：根节点为组合类型，子节点为基础类型（通过懒加载）
        """
        # 如果是懒加载子节点（传入了 composite_type_id），去除分页参数
        composite_type_id = request.query_params.get('composite_type_id', None)
        if composite_type_id:
            # 懒加载子节点时，去除分页参数，返回所有子节点
            request.query_params._mutable = True
            if 'page' in request.query_params:
                del request.query_params['page']
            if 'limit' in request.query_params:
                del request.query_params['limit']
        
        response = super().list(request, *args, **kwargs)
        
        # 处理返回数据，添加 hasChild 字段
        if response.data:
            # 处理分页数据格式
            if 'results' in response.data:
                results = response.data['results']
                for item in results:
                    if item.get('is_composite'):
                        # 检查该组合类型是否有子节点（基础类型）
                        has_child = AdMediaTypeCompositionModel.objects.filter(
                            composite_type_id=item['id'],
                            delete_mark=0
                        ).exists()
                        item['hasChild'] = has_child
                    else:
                        # 基础类型没有子节点
                        item['hasChild'] = False
            # 处理直接返回列表格式（非分页）
            elif isinstance(response.data, list):
                for item in response.data:
                    if item.get('is_composite'):
                        has_child = AdMediaTypeCompositionModel.objects.filter(
                            composite_type_id=item['id'],
                            delete_mark=0
                        ).exists()
                        item['hasChild'] = has_child
                    else:
                        item['hasChild'] = False
            # 处理 data 字段是数组的情况（某些情况下可能直接返回数组）
            elif isinstance(response.data, dict) and 'data' in response.data:
                if isinstance(response.data['data'], list):
                    for item in response.data['data']:
                        if item.get('is_composite'):
                            has_child = AdMediaTypeCompositionModel.objects.filter(
                                composite_type_id=item['id'],
                                delete_mark=0
                            ).exists()
                            item['hasChild'] = has_child
                        else:
                            item['hasChild'] = False
        
        return response
