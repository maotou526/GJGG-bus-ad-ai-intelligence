'''
Description: 预订订单明细视图
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from rest_framework.decorators import action
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import BookingOrderDetailModel
from .serializers import (
    BookingOrderDetailModelSerializer,
    BookingOrderDetailModelCreateSerializer,
    BookingOrderDetailModelUpdateSerializer,
    BookingOrderDetailModelListSerializer
)
from django.db.models import Q


class BookingOrderDetailModelViewSet(CustomModelViewSet):
    """
    预订订单明细管理视图集
    
    功能说明:
    - 提供预订订单明细的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作
    
    标准DRF接口:
    - GET /api/BookingOrderDetailModelViewSet/ - 获取预订订单明细列表
    - POST /api/BookingOrderDetailModelViewSet/ - 创建预订订单明细
    - PUT /api/BookingOrderDetailModelViewSet/{id}/ - 更新预订订单明细
    - DELETE /api/BookingOrderDetailModelViewSet/{id}/ - 删除预订订单明细
    """
    # 查询集
    queryset = BookingOrderDetailModel.objects.all()
    
    # 默认序列化器(用于查询详情)
    serializer_class = BookingOrderDetailModelSerializer
    
    # 列表序列化器(用于列表展示)
    list_serializer_class = BookingOrderDetailModelListSerializer
    
    # 创建序列化器
    create_serializer_class = BookingOrderDetailModelCreateSerializer
    
    # 更新序列化器
    update_serializer_class = BookingOrderDetailModelUpdateSerializer
    
    # 过滤字段(支持精确查询)
    filter_fields = [
        'id', 'booking_order_id', 'roadline_id', 'roadline_name',
        'roadline_company_id', 'media_type_id', 'is_composite',
        'lock_status', 'enabled_mark', 'delete_mark'
    ]
    
    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        'id', 'booking_order_id', 'roadline_id', 'roadline_name',
        'roadline_company_id', 'media_type_id', 'is_composite',
        'lock_status', 'enabled_mark', 'delete_mark'
    ]
    
    # 搜索字段(支持模糊查询)
    search_fields = ['roadline_name', 'roadline_company_name', 'media_type_name']
    
    # 排序字段
    ordering_fields = ['create_datetime', 'update_datetime', 'quantity', 'subtotal_amount']
    
    # 默认排序
    ordering = ['booking_order_id', 'roadline_id', 'media_type_id']
