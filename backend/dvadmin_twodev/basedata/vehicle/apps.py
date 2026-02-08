'''
Description: 车辆应用配置
Version: 1.0
Autor: 王晨
Date: 2025-10-18
LastEditors: 王晨
LastEditTime: 2025-10-18
'''
from django.apps import AppConfig


class VehicleConfig(AppConfig):
    default_auto_field = "django.db.models.AutoField"
    name = "dvadmin_twodev.basedata.vehicle"
