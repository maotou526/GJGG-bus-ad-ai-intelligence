'''
Description: 分表工具方法
Version: 1.0
Author: 王晨
Date: 2025-11-26
LastEditors: 王晨
LastEditTime: 2025-12-11 09:34:21
'''
from datetime import datetime, date, timedelta
from typing import Dict, Iterator, Type, Union

from django.db import models, connection

from .sharding import ShardingConfig

# 缓存已经创建的代理模型，避免重复构造
_PROXY_MODEL_CACHE: Dict[str, Type[models.Model]] = {}
DATE_TYPES = (str, date, datetime)


def get_sharding_proxy_model(
    model_or_instance,
    date_or_table: Union[str, date, datetime, None] = None,
) -> Type[models.Model]:
    """
    根据日期获取对应分表的代理模型
    
    如果对应的分表不存在，返回一个安全的代理模型，其查询会返回空查询集，
    而不是抛出异常。

    Args:
        model_or_instance: 原始模型类或模型实例
        date_or_table: 日期值（str/date/datetime）或分表名（str），用于确定目标表

    Returns:
        Type[models.Model]: 指向目标分表的代理模型（如果表不存在，返回安全的代理模型）
    """
    if isinstance(model_or_instance, models.Model):
        model = model_or_instance.__class__
        if date_or_table is None:
            date_or_table = getattr(model_or_instance, getattr(model, "sharding_config", {}).get("date_field", "stat_date"), None)
    else:
        model = model_or_instance

    config = ShardingConfig(model, getattr(model, "sharding_config", None))

    if date_or_table and isinstance(date_or_table, str) and date_or_table.startswith(config.get_base_table() + "_"):
        table_name = date_or_table
    else:
        date_value = date_or_table
        if date_value is None:
            raise ValueError("获取分表代理模型需要提供日期值或分表表名")
        table_name = config.get_table_name(date_value)
    
    cache_key = f"{model.__module__}.{model.__name__}:{table_name}"
    
    # 检查缓存
    if cache_key in _PROXY_MODEL_CACHE:
        return _PROXY_MODEL_CACHE[cache_key]
    
    # 检查表是否存在
    table_exists = _table_exists(table_name)
    
    class Meta:
        proxy = True
        app_label = model._meta.app_label

    proxy_model = type(
        f"{model.__name__}_Shard_{table_name.replace('.', '_')}",
        (model,),
        {
            "__module__": model.__module__,
            "Meta": Meta,
        },
    )
    proxy_model._meta.db_table = table_name
    
    # 如果表不存在，创建一个返回空查询集的 Manager
    if not table_exists:
        class EmptyManager(models.Manager):
            """返回空查询集的 Manager"""
            def get_queryset(self):
                return model.objects.none()
            
            def all(self):
                return self.get_queryset()
            
            def filter(self, *args, **kwargs):
                return self.get_queryset()
            
            def exclude(self, *args, **kwargs):
                return self.get_queryset()
            
            def first(self):
                return None
            
            def last(self):
                return None
            
            def count(self):
                return 0
            
            def exists(self):
                return False
        
        # 创建 Manager 实例并显式绑定到代理模型
        manager = EmptyManager()
        manager.contribute_to_class(proxy_model, 'objects')
    else:
        # 表存在，使用普通的 Manager
        # 如果原模型有自定义 manager（如 ShardingManager），使用普通的 Manager 避免递归
        # 创建 Manager 实例并显式绑定到代理模型
        manager = models.Manager()
        manager.contribute_to_class(proxy_model, 'objects')
    
    _PROXY_MODEL_CACHE[cache_key] = proxy_model
    return proxy_model

def iter_sharding_range(
    model: Type[models.Model],
    start_date: Union[str, date, datetime],
    end_date: Union[str, date, datetime],
    **filters,
) -> Iterator[models.Model]:
    """
    按日期范围遍历分表数据（按日分表场景）

    Args:
        model: 分表模型类
        start_date: 起始日期
        end_date: 结束日期
        filters: 额外过滤条件，例如 company_no='xxx'

    Yields:
        models.Model: 每条符合条件的记录
    """
    config = ShardingConfig(model, getattr(model, "sharding_config", None))
    date_field = config.get_date_field()
    start = _normalize_date(start_date)
    end = _normalize_date(end_date)
    if start > end:
        start, end = end, start

    current = start
    while current <= end:
        # 计算当前日期对应的分表名
        table_name = config.get_table_name(current)

        # 如果分表不存在，则跳过该日期，相当于该日数据为空
        if not _table_exists(table_name):
            current += timedelta(days=1)
            continue

        # 获取指向该分表的代理模型
        proxy_model = get_sharding_proxy_model(model, table_name)

        # 查询当前日期的数据
        queryset = proxy_model.objects.filter(**{date_field: current}, **filters).order_by("id")
        yield from queryset.iterator()
        current += timedelta(days=1)


def _normalize_date(value: Union[str, date, datetime]) -> date:
    """将不同类型的日期值统一转为 date"""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").date()
    raise ValueError(f"无法解析的日期类型: {type(value)}")


def _table_exists(table_name: str) -> bool:
    """
    检查分表是否存在
    与 mixins.ShardingTableMixin._check_table_exists 保持一致逻辑：
    - 先查 information_schema.tables
    - 再查 pg_catalog.pg_class（兼容 Vastbase / PostgreSQL）
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_schema()")
            schema = cursor.fetchone()[0] or 'public'

            # information_schema 检查
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

            # pg_catalog 兜底检查
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

