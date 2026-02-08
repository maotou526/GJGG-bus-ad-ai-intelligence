'''
Description: 公交线路复线情况应用配置
Version: 1.0
Author: 王晨
Date: 2025-01-XX
LastEditors: 王晨
LastEditTime: 2025-11-27 14:15:57
'''
from django.apps import AppConfig


class RoadlineToRoadlineOverlapConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "dvadmin_twodev.line_overlap.roadline_to_roadline_overlap"
    verbose_name = "公交线路复线管理"
