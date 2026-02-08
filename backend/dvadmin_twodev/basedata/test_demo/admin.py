'''
Description: 环域信息管理后台配置
Version: 1.0
Author: CursorAgent
Date: 2025-11-10 00:00:00
LastEditors: CursorAgent
LastEditTime: 2025-11-10 00:00:00
'''
from django.contrib import admin

from .models import DcBaseTorusinfoModel


@admin.register(DcBaseTorusinfoModel)
class DcBaseTorusinfoModelAdmin(admin.ModelAdmin):
    """
    环域信息模型后台管理配置
    """

    list_display = ("id", "explain", "torus", "remarks", "enabled_mark", "delete_mark", "create_date")
    search_fields = ("id", "explain", "remarks")
    list_filter = ("enabled_mark", "delete_mark", "create_date")
