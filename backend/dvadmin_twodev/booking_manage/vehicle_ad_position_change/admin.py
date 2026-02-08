'''
Description: 车位广告变更历史后台管理
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.contrib import admin

from .models import VehicleAdPositionChangeModel


@admin.register(VehicleAdPositionChangeModel)
class VehicleAdPositionChangeModelAdmin(admin.ModelAdmin):
    """车位广告变更历史后台管理"""

    list_display = [
        "id",
        "booking_order_id",
        "booking_detail_id",
        "action_type",
        "position_id",
        "roadline_id",
        "roadline_name",
        "roadline_company_id",
        "roadline_company_name",
        "vehicle_id",
        "vehicle_no",
        "resource_id",
        "change_node",
        "operator_id",
        "operation_time",
        "enabled_mark",
    ]
    list_filter = [
        "action_type",
        "roadline_id",
        "roadline_company_id",
        "vehicle_id",
        "resource_id",
        "change_node",
        "operator_id",
        "enabled_mark",
        "delete_mark",
    ]
    search_fields = ["roadline_name", "roadline_company_name", "vehicle_no"]
    ordering = ["-operation_time"]
