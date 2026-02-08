'''
Description: 媒体类型组合关系视图
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse
from rest_framework.decorators import action
from .models import AdMediaTypeCompositionModel
from .serializers import AdMediaTypeCompositionModelSerializer


class AdMediaTypeCompositionModelViewSet(CustomModelViewSet):
    """
    媒体类型组合关系管理视图集
    提供标准CRUD接口
    """
    queryset = AdMediaTypeCompositionModel.objects.all()
    serializer_class = AdMediaTypeCompositionModelSerializer
    
    def create(self, request, *args, **kwargs):
        """创建组合关系"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"=== 创建组合关系 ===")
        logger.info(f"请求数据: {request.data}")
        logger.info(f"请求方法: {request.method}")
        logger.info(f"请求路径: {request.path}")
        return super().create(request, *args, **kwargs)
    
    # 配置基本的过滤和搜索字段
    filterset_fields = ['composite_type_id', 'component_type_id', 'enabled_mark', 'delete_mark']
    search_fields = []
    
    def get_queryset(self):
        """
        自定义查询集
        """
        queryset = super().get_queryset()
        
        # 处理组合类型ID过滤
        composite_type_id = self.request.query_params.get('composite_type_id', None)
        if composite_type_id:
            queryset = queryset.filter(composite_type_id=composite_type_id)
        
        # 处理基础类型ID过滤
        component_type_id = self.request.query_params.get('component_type_id', None)
        if component_type_id:
            queryset = queryset.filter(component_type_id=component_type_id)
        
        return queryset
    
    @action(detail=False, methods=['post'])
    def batch_save(self, request):
        """
        批量保存组合关系
        请求数据格式：
        {
            "composite_type_id": "组合类型ID",
            "compositions": [
                {
                    "component_type_id": "基础类型ID",
                    "sort_order": 1
                },
                ...
            ]
        }
        """
        composite_type_id = request.data.get('composite_type_id')
        compositions = request.data.get('compositions', [])
        
        if not composite_type_id:
            return ErrorResponse(msg='组合类型ID不能为空')
        
        if not isinstance(compositions, list):
            return ErrorResponse(msg='组合关系数据格式错误')
        
        try:
            # 删除该组合类型的所有旧关系（软删除）
            AdMediaTypeCompositionModel.objects.filter(
                composite_type_id=composite_type_id,
                delete_mark=0
            ).update(delete_mark=1)
            
            # 创建新的组合关系
            created_items = []
            for comp in compositions:
                component_type_id = comp.get('component_type_id')
                sort_order = comp.get('sort_order')
                
                if not component_type_id:
                    continue
                
                # 检查是否已存在（包括已删除的）
                existing = AdMediaTypeCompositionModel.objects.filter(
                    composite_type_id=composite_type_id,
                    component_type_id=component_type_id
                ).first()
                
                if existing:
                    # 恢复并更新
                    existing.delete_mark = 0
                    existing.sort_order = sort_order
                    # 更新修改人信息
                    if request.user and str(request.user) != "AnonymousUser":
                        existing.modifier = request.user
                        existing.modifier_name = getattr(request.user, 'name', '')
                    existing.save()
                    created_items.append(existing)
                else:
                    # 创建新的
                    create_data = {
                        'composite_type_id': composite_type_id,
                        'component_type_id': component_type_id,
                        'sort_order': sort_order,
                        'enabled_mark': 1,
                        'delete_mark': 0
                    }
                    # 设置创建人和修改人信息
                    if request.user and str(request.user) != "AnonymousUser":
                        create_data['creator'] = request.user
                        create_data['modifier'] = request.user
                        create_data['creator_name'] = getattr(request.user, 'name', '')
                        create_data['modifier_name'] = getattr(request.user, 'name', '')
                    new_item = AdMediaTypeCompositionModel.objects.create(**create_data)
                    created_items.append(new_item)
            
            return SuccessResponse(data={
                'composite_type_id': composite_type_id,
                'count': len(created_items),
                'items': AdMediaTypeCompositionModelSerializer(created_items, many=True).data
            }, msg='保存成功')
            
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f'批量保存组合关系失败: {str(e)}')
            return ErrorResponse(msg=f'保存失败: {str(e)}')