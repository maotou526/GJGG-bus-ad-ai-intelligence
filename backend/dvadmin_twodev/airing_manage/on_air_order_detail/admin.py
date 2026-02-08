from django.contrib import admin
from .models import OnAirOrderDetailModel


@admin.register(OnAirOrderDetailModel)
class OnAirOrderDetailModelAdmin(admin.ModelAdmin):
    """上刊订单明细管理后台"""
    list_display = [
        "id",
        "order_id",
        "position_id",
        "roadline_name",
        "roadline_company_name",
        "plan_vehicle_no",
        "act_vehicle_no",
        "base_media_type_name",
        "execution_status",
        "act_on_air_datetime",
        "create_datetime",
    ]
    list_filter = ["execution_status", "enabled_mark", "delete_mark"]
    search_fields = ["roadline_name", "roadline_company_name", "plan_vehicle_no", "act_vehicle_no"]
    readonly_fields = ["id", "create_datetime", "update_datetime"]
