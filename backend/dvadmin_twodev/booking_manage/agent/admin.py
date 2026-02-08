'''
Description: 代理商后台管理
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.contrib import admin
from .models import AgentModel


@admin.register(AgentModel)
class AgentModelAdmin(admin.ModelAdmin):
    """代理商后台管理"""
    list_display = [
        'id', 'agent_code', 'company_name', 'credit_code', 'legal_person',
        'cooperation_level', 'contract_start_date', 'contract_end_date', 'enabled_mark'
    ]
    list_filter = ['cooperation_level', 'settlement_type', 'enabled_mark', 'delete_mark']
    search_fields = ['agent_code', 'company_name', 'credit_code', 'legal_person', 'contact_phone']
    ordering = ['company_name']
