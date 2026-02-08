'''
Description: 代理商资源授权后台管理
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.contrib import admin
from .models import AgentResourceAuthModel


@admin.register(AgentResourceAuthModel)
class AgentResourceAuthModelAdmin(admin.ModelAdmin):
    """代理商资源授权后台管理"""
    list_display = [
        'id', 'agent_id', 'resource_type', 'resource_id',
        'auth_start_date', 'auth_end_date', 'enabled_mark'
    ]
    list_filter = ['resource_type', 'enabled_mark', 'delete_mark', 'auth_start_date', 'auth_end_date']
    search_fields = ['agent_id__company_name', 'agent_id__agent_code']
    ordering = ['agent_id', 'resource_type', 'resource_id']
    raw_id_fields = ['agent_id']
