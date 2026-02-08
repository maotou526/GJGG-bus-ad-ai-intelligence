'''
Description: 预订订单明细后台管理
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.contrib import admin
from .models import BookingOrderDetailModel


@admin.register(BookingOrderDetailModel)
class BookingOrderDetailModelAdmin(admin.ModelAdmin):
    """预订订单明细后台管理"""
    list_display = [
        'id', 'booking_order_id', 'roadline_name', 'roadline_company_name',
        'media_type_name', 'is_composite', 'quantity', 'unit_price', 'subtotal_amount', 'lock_status'
    ]
    list_filter = ['booking_order_id', 'roadline_company_id', 'is_composite', 'lock_status', 'enabled_mark', 'delete_mark']
    search_fields = ['roadline_name', 'roadline_company_name', 'media_type_name']
    ordering = ['booking_order_id', 'roadline_id', 'media_type_id']
