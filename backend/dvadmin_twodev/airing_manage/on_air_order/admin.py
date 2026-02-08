from django.contrib import admin
from .models import OnAirOrderModel


@admin.register(OnAirOrderModel)
class OnAirOrderModelAdmin(admin.ModelAdmin):
    """上刊订单管理后台"""
    list_display = [
        "id",
        "order_no",
        "booking_order_id",
        "customer_name",
        "booking_start_date",
        "booking_end_date",
        "order_status",
        "approved_time",
        "create_datetime",
    ]
    list_filter = ["order_status", "enabled_mark", "delete_mark"]
    search_fields = ["order_no", "customer_name"]
    readonly_fields = ["id", "create_datetime", "update_datetime"]
