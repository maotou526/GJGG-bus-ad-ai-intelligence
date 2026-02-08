'''
Description: 站点关联应用配置
Version: 1.0
Autor: 王晨
Date: 2025-10-14
LastEditors: 王晨
LastEditTime: 2025-10-14
'''
from django.apps import AppConfig


class RoadlineStopRelConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "dvadmin_twodev.basedata.roadline_stop_rel"
    verbose_name = "站点关联管理"