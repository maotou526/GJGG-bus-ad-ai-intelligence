'''
Description: 分表 ViewSet Mixin
Version: 1.0
Author: 王晨
Date: 2025-11-26
LastEditors: 王晨
LastEditTime: 2025-11-26
'''
from datetime import datetime
from django.db import connection
from dvadmin_extensions.table_sharding.sharding import ShardingConfig


class ShardingTableMixin:
    """
    分表 ViewSet Mixin

    通过动态代理模型实现分表查询，避免修改原模型的 _meta.db_table。
    
    核心原理：
    Django ORM 的 Query 对象会在 QuerySet 创建时缓存表别名(alias_map)。
    如果直接修改 model._meta.db_table，已创建的 QuerySet 不会更新其内部缓存，
    导致 FROM 和 WHERE 使用不同的表名。
    
    解决方案：
    为每个分表创建一个动态代理模型，这个代理模型有自己独立的 _meta.db_table，
    不会与原模型冲突。
    """

    sharding_date_param = None  # 可覆盖默认的日期参数名
    _sharding_proxy_models = {}  # 缓存动态代理模型

    def initial(self, request, *args, **kwargs):
        """在请求处理开始时解析分表参数"""
        super().initial(request, *args, **kwargs)
        
        model = self.queryset.model if hasattr(self, 'queryset') and self.queryset is not None else None
        if model is None or not hasattr(model, 'sharding_config'):
            return

        config = ShardingConfig(model, model.sharding_config)
        date_field = config.config.get('date_field', 'stat_date')
        base_table = config.config.get('base_table')
        param_name = self.sharding_date_param or date_field

        # 保存配置信息（供后续方法使用）
        request._sharding_date_field = date_field
        request._sharding_base_table = base_table
        request._sharding_config = config
        request._sharding_model = model

        # 对于 update/partial_update 操作，延迟到 update 方法中处理
        # 因为 initial() 在请求体解析之前调用，此时 request.data 可能还没准备好
        if self.action in ('update', 'partial_update'):
            request._sharding_defer_to_update = True
            return

        # 尝试从 URL 查询参数获取日期值
        date_value = request.query_params.get(param_name)
        
        if not date_value:
            # 没有日期参数，使用基础表
            request._sharding_target_table = base_table
            return

        self._setup_sharding_table(request, date_value, config, date_field)

    def _setup_sharding_table(self, request, date_value, config, date_field):
        """
        根据日期值设置分表信息
        """
        try:
            if isinstance(date_value, str):
                date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
        except ValueError:
            request._sharding_target_table = request._sharding_base_table
            return

        table_name = config.get_table_name(date_value)

        if not self._check_table_exists(table_name):
            request._sharding_table_not_exists = {
                'table_name': table_name,
                'date_value': date_value,
                'date_field': date_field,
            }
            return

        # 保存目标表名
        request._sharding_target_table = table_name

    def get_queryset(self):
        """
        获取 QuerySet，使用动态代理模型实现分表查询。
        """
        request = getattr(self, 'request', None)
        model = self.queryset.model if hasattr(self, 'queryset') and self.queryset is not None else None
        
        if model is None:
            return super().get_queryset()
        
        # 如果分表不存在，返回空查询集
        if request and hasattr(request, '_sharding_table_not_exists'):
            return model.objects.none()
        
        # 检查是否有分表配置
        if not hasattr(model, 'sharding_config'):
            return super().get_queryset()
        
        # 获取目标表名
        target_table = getattr(request, '_sharding_target_table', None)
        base_table = getattr(request, '_sharding_base_table', None)
        
        if not target_table or target_table == base_table:
            # 使用基础表，调用父类的 get_queryset 以应用其他过滤逻辑
            return super().get_queryset()
        
        # 创建或获取动态代理模型
        proxy_model = self._get_or_create_proxy_model(model, target_table)
        
        # 临时替换 self.queryset 的模型为代理模型
        original_queryset = self.queryset
        self.queryset = proxy_model._default_manager.all()
        
        try:
            # 调用父类的 get_queryset，这样会应用 CustomModelViewSet 的过滤逻辑
            result_queryset = super().get_queryset()
            return result_queryset
        finally:
            # 恢复原始 queryset
            self.queryset = original_queryset

    def _get_or_create_proxy_model(self, model, table_name):
        """
        创建或获取动态代理模型。
        
        为每个分表创建一个独立的代理模型，这个代理模型有自己的 _meta.db_table，
        不会影响原模型。
        """
        cache_key = f"{model.__name__}_{table_name}"
        
        if cache_key not in self._sharding_proxy_models:
            # 动态创建代理模型
            class Meta:
                proxy = True
                db_table = table_name
                app_label = model._meta.app_label
            
            # 创建代理模型类
            proxy_model = type(
                f"{model.__name__}_{table_name.replace('.', '_')}",
                (model,),
                {
                    '__module__': model.__module__,
                    'Meta': Meta,
                }
            )
            
            # 手动设置 _meta.db_table（因为动态创建的类可能不会正确继承）
            proxy_model._meta.db_table = table_name
            
            self._sharding_proxy_models[cache_key] = proxy_model
        
        return self._sharding_proxy_models[cache_key]

    def _check_table_exists(self, table_name: str) -> bool:
        """检查分表是否存在"""
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_schema()")
                schema = cursor.fetchone()[0] or 'public'

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM information_schema.tables
                    WHERE table_schema = %s
                    AND LOWER(table_name) = LOWER(%s)
                    """,
                    [schema, table_name],
                )
                exists = cursor.fetchone()[0] > 0
                if exists:
                    return True

                cursor.execute(
                    """
                    SELECT COUNT(*)
                    FROM pg_catalog.pg_class c
                    JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
                    WHERE n.nspname = %s
                    AND c.relname = %s
                    AND c.relkind = 'r'
                    """,
                    [schema, table_name],
                )
                return cursor.fetchone()[0] > 0
        except Exception:
            return False

