'''
Description: 车辆后台管理
Version: 1.0
Autor: 王晨
Date: 2025-10-18
LastEditors: 王晨
LastEditTime: 2025-10-18
'''
from django.contrib import admin
from .models import VehicleModel


@admin.register(VehicleModel)
class VehicleModelAdmin(admin.ModelAdmin):
    """车辆后台管理"""
    list_display = ['id', 'vehicle_plate', 'vehicle_no', 'company_name', 'branch', 'roadline', 'vehicle_brand', 'is_new_energy', 'enabled_mark']
    list_filter = ['is_new_energy', 'is_baofei', 'new_flag', 'enabled_mark', 'company_name', 'branch']
    search_fields = ['vehicle_plate', 'vehicle_no', 'company_name', 'vehicle_brand', 'vehicle_type']
    ordering = ['vehicle_plate']
