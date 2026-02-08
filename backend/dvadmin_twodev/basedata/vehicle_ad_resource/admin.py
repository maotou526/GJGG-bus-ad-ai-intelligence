'''
Description: 车辆广告资源位后台管理
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.contrib import admin
from .models import VehicleAdResourceModel


@admin.register(VehicleAdResourceModel)
class VehicleAdResourceModelAdmin(admin.ModelAdmin):
    """车辆广告资源位后台管理"""
    list_display = [
        'id', 'resource_code', 'vehicle_id', 'base_media_type_id', 
        'resource_status', 'current_order_id', 'on_air_date', 'off_air_date', 'enabled_mark'
    ]
    list_filter = ['resource_status', 'enabled_mark', 'delete_mark', 'on_air_date', 'off_air_date']
    search_fields = ['resource_code', 'remark', 'vehicle_id__vehicle_plate', 'vehicle_id__vehicle_no']
    ordering = ['vehicle_id', 'base_media_type_id']
    raw_id_fields = ['vehicle_id', 'base_media_type_id']
