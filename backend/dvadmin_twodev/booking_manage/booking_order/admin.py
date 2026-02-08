'''
Description: 预订订单后台管理
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.contrib import admin
from .models import BookingOrderModel


@admin.register(BookingOrderModel)
class BookingOrderModelAdmin(admin.ModelAdmin):
    """预订订单后台管理"""
    list_display = [
        'id', 'booking_no', 'customer_name', 'booking_type', 'booking_status',
        'start_date', 'end_date', 'total_amount', 'paid_amount', 'enabled_mark'
    ]
    list_filter = ['booking_type', 'booking_status', 'start_date', 'end_date', 'enabled_mark', 'delete_mark']
    search_fields = ['booking_no', 'customer_name', 'ad_content']
    ordering = ['-create_datetime']

