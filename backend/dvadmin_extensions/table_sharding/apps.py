'''
Description: 分表管理扩展应用配置
Version: 1.0
Author: 王晨
Date: 2025-11-26
LastEditors: 王晨
LastEditTime: 2025-11-26
'''
from django.apps import AppConfig


class TableShardingConfig(AppConfig):
    """分表管理扩展应用配置"""
    name = 'dvadmin_extensions.table_sharding'
    verbose_name = '分表管理扩展'
    
    def ready(self):
        """
        应用就绪时的初始化
        
        注意：分表切换逻辑已移至 ShardingTableMixin.get_queryset()，
        不再需要全局注册 ShardingTableFilter。
        使用分表功能的 ViewSet 需要继承 ShardingTableMixin。
        """
        pass
