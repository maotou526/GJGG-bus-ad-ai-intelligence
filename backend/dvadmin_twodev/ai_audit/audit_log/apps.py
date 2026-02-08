"""
AI审核记录应用配置
Description: Django应用配置
Version: 1.0
Date: 2026-02-03
"""
from django.apps import AppConfig


class AuditLogConfig(AppConfig):
    """AI审核记录应用配置"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dvadmin_twodev.ai_audit.audit_log'
    verbose_name = 'AI审核记录'
