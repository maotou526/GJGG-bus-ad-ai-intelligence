"""
数据权限扩展应用配置
"""
from django.apps import AppConfig


class DataPermissionConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dvadmin_extensions.data_permission'
    verbose_name = '数据权限扩展'
    
    def ready(self):
        """
        应用就绪时的初始化
        自动注册扩展的过滤器到原框架
        """
        self._register_custom_filter()
    
    def _register_custom_filter(self):
        """注册自定义规则过滤器到原框架的 ViewSet"""
        try:
            from dvadmin.utils import viewset
            from .filters import CustomRuleDataPermissionFilter
            
            # 检查是否已注册
            if CustomRuleDataPermissionFilter not in viewset.CustomModelViewSet.extra_filter_class:
                # 插入到最前面，确保优先级最高
                viewset.CustomModelViewSet.extra_filter_class.insert(
                    0,
                    CustomRuleDataPermissionFilter
                )
                
                import logging
                logger = logging.getLogger(__name__)
                logger.info("✅ 自定义数据权限过滤器已注册")
        
        except Exception as e:
            import warnings
            warnings.warn(f"注册自定义数据权限过滤器失败: {e}")

