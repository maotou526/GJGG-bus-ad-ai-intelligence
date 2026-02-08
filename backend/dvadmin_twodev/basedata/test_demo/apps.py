'''
Description: 测试演示应用配置
Version: 1.0
Author: CursorAgent
Date: 2025-11-10 00:00:00
LastEditors: CursorAgent
LastEditTime: 2025-11-10 00:00:00
'''
from django.apps import AppConfig


class TestDemoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dvadmin_twodev.basedata.test_demo"
    verbose_name = "测试演示"
    
    def ready(self):
        """应用准备就绪时设置模型的 db_label"""
        from .models import DcBaseTorusinfoModel
        # 在应用完全初始化后设置 db_label
        DcBaseTorusinfoModel._meta.db_label = "dm"
