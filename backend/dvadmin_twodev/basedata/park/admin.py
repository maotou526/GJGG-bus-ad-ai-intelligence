'''
Description: 停车场站后台管理
Version: 1.0
Autor: 王晨
Date: 2025-10-18
LastEditors: 王晨
LastEditTime: 2025-10-18
'''
from django.contrib import admin
from .models import ParkModel


@admin.register(ParkModel)
class ParkModelAdmin(admin.ModelAdmin):
    """停车场站后台管理"""
    list_display = ['id', 'park_name', 'company_name', 'park_code', 'park_type', 'park_status', 'enabled_mark']
    list_filter = ['park_type', 'station_type', 'park_status', 'enabled_mark']
    search_fields = ['park_name', 'company_name', 'park_code', 'principal']
    ordering = ['park_name']
