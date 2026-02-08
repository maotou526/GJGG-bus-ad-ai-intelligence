'''
Description: 客户后台管理
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.contrib import admin
from .models import CustomerModel


@admin.register(CustomerModel)
class CustomerModelAdmin(admin.ModelAdmin):
    """客户后台管理"""
    list_display = [
        'id', 'customer_code', 'company_name', 'credit_code', 'contact_name',
        'industry', 'customer_level', 'status', 'agent_id', 'enabled_mark'
    ]
    list_filter = ['industry', 'customer_level', 'status', 'agent_id', 'enabled_mark', 'delete_mark']
    search_fields = ['customer_code', 'company_name', 'credit_code', 'contact_name', 'contact_phone']
    ordering = ['company_name']
