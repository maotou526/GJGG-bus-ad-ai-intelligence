'''
Description: 车位广告后台管理
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.contrib import admin

from .models import VehicleAdPositionModel


@admin.register(VehicleAdPositionModel)
class VehicleAdPositionModelAdmin(admin.ModelAdmin):
    """车位广告后台管理"""

    list_display = [
        "id",
        "booking_detail_id",
        "roadline_id",
        "roadline_name",
        "roadline_company_id",
        "roadline_company_name",
        "resource_id",
        "vehicle_id",
        "vehicle_no",
        "reserved_start_date",
        "reserved_end_date",
        "actual_on_date",
        "actual_off_date",
        "allocation_status",
        "enabled_mark",
    ]
    list_filter = [
        "roadline_id",
        "roadline_company_id",
        "vehicle_id",
        "allocation_status",
        "enabled_mark",
        "delete_mark",
    ]
    search_fields = ["vehicle_no", "roadline_name", "roadline_company_name"]
    ordering = ["booking_detail_id"]
