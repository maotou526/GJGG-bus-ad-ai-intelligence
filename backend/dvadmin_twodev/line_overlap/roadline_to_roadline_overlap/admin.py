'''
Description: 公交线路复线情况Admin配置
Version: 1.0
Author: 王晨
Date: 2025-01-XX
LastEditors: 
LastEditTime: 
'''
from django.contrib import admin
from .models import RoadlineToRoadlineOverlapModel


@admin.register(RoadlineToRoadlineOverlapModel)
class RoadlineToRoadlineOverlapAdmin(admin.ModelAdmin):
    list_display = ['id', 'main_roadline_name', 'vice_roadline_name', 'repeat_line_length', 'exec_day']
    list_filter = ['exec_day', 'expiry_day']
    search_fields = ['main_roadline_name', 'vice_roadline_name', 'main_roadline_code', 'vice_roadline_code']
