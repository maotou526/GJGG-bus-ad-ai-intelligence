'''
Description: Django 通用分表框架核心实现
Version: 1.0
Author: 王晨
Date: 2025-11-26
LastEditors: 王晨
LastEditTime: 2025-12-26 14:29:08
'''
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from collections import defaultdict
from django.db import models, connection
from django.db.models import QuerySet, Manager
from django.core.exceptions import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)


class ShardingConfig:
    """分表配置类"""
    
    # 默认配置
    DEFAULT_CONFIG = {
        'date_field': 'create_datetime',  # 默认使用创建时间
        'shard_type': 'month',            # 默认按月分表
        'base_table': None,               # 基础表名（从模型Meta获取）
        'auto_create_table': True,        # 自动创建分表
    }
    
    # 分表类型映射
    SHARD_TYPE_FORMAT = {
        'year': '%Y',           # 按年：2025
        'month': '%Y%m',        # 按月：202501
        'day': '%Y%m%d',        # 按日：20250115
    }
    
    def __init__(self, model, config: Optional[Dict[str, Any]] = None):
        """
        初始化分表配置
        
        Args:
            model: Django模型类
            config: 分表配置字典
        """
        self.model = model
        self.config = {**self.DEFAULT_CONFIG, **(config or {})}
        
        # 从模型Meta获取基础表名
        if not self.config['base_table']:
            self.config['base_table'] = model._meta.db_table
        
        # 验证配置
        self._validate_config()
    
    def _validate_config(self):
        """验证配置有效性"""
        # 验证分表类型
        if self.config['shard_type'] not in self.SHARD_TYPE_FORMAT:
            raise ImproperlyConfigured(
                f"分表类型必须是: {list(self.SHARD_TYPE_FORMAT.keys())}"
            )
        
        # 验证日期字段是否存在
        date_field = self.config['date_field']
        if not hasattr(self.model, date_field):
            raise ImproperlyConfigured(
                f"模型 {self.model.__name__} 没有字段: {date_field}"
            )
    
    def get_shard_suffix(self, date_value) -> str:
        """
        根据日期获取分表后缀
        
        Args:
            date_value: 日期值（date/datetime/str）
            
        Returns:
            str: 分表后缀，如 '202501'
        """
        # 转换为date对象
        if isinstance(date_value, str):
            try:
                date_value = datetime.strptime(date_value, '%Y-%m-%d').date()
            except ValueError:
                try:
                    date_value = datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S').date()
                except ValueError:
                    raise ValueError(f"无法解析日期格式: {date_value}")
        elif isinstance(date_value, datetime):
            date_value = date_value.date()
        elif not isinstance(date_value, date):
            raise ValueError(f"不支持的日期类型: {type(date_value)}")
        
        # 根据分表类型格式化
        shard_type = self.config['shard_type']
        format_str = self.SHARD_TYPE_FORMAT[shard_type]
        return date_value.strftime(format_str)
    
    def get_table_name(self, date_value) -> str:
        """
        获取完整的分表名
        
        Args:
            date_value: 日期值
            
        Returns:
            str: 完整表名，如 'od_details_202501'
        """
        suffix = self.get_shard_suffix(date_value)
        return f"{self.config['base_table']}_{suffix}"
    
    def get_date_field(self) -> str:
        """获取日期字段名"""
        return self.config['date_field']
    
    def get_base_table(self) -> str:
        """获取基础表名"""
        return self.config['base_table']


class ShardingQuerySet(QuerySet):
    """分表查询集"""
    
    def __init__(self, model=None, query=None, using=None, hints=None):
        super().__init__(model, query, using, hints)
        self._shard_table = None  # 当前使用的分表名
        self._shard_config = None  # 分表配置对象
    
    def _get_shard_config(self):
        """获取分表配置"""
        if self._shard_config is None:
            model = self.model
            # 从模型获取分表配置
            sharding_config = getattr(model, 'sharding_config', None)
            self._shard_config = ShardingConfig(model, sharding_config)
        return self._shard_config
    
    def _switch_table(self, table_name: str):
        """
        切换模型使用的表名
        
        Args:
            table_name: 目标表名
        """
        if self._shard_table != table_name:
            self.model._meta.db_table = table_name
            self._shard_table = table_name
            logger.debug(f"切换到分表: {table_name}")
    
    def _restore_table(self):
        """恢复原始表名"""
        if self._shard_table:
            config = self._get_shard_config()
            self.model._meta.db_table = config.get_base_table()
            self._shard_table = None
    
    def filter(self, *args, **kwargs):
        """
        重写 filter 方法，自动检测 stat_date 字段并路由到对应分表
        """
        config = self._get_shard_config()
        date_field = config.get_date_field()
        
        # 检查是否有日期字段的过滤条件
        if date_field in kwargs:
            # 精确匹配：stat_date=某个日期
            date_value = kwargs[date_field]
            if date_value:
                table_name = config.get_table_name(date_value)
                self._switch_table(table_name)
        elif f'{date_field}__exact' in kwargs:
            # 精确匹配：stat_date__exact=某个日期
            date_value = kwargs[f'{date_field}__exact']
            if date_value:
                table_name = config.get_table_name(date_value)
                self._switch_table(table_name)
        elif f'{date_field}__gte' in kwargs or f'{date_field}__lte' in kwargs:
            # 范围查询：stat_date__gte 或 stat_date__lte
            start_date = kwargs.get(f'{date_field}__gte')
            end_date = kwargs.get(f'{date_field}__lte')
            
            if start_date and end_date:
                # 有开始和结束日期，使用范围查询
                return self.filter_by_date_range(start_date, end_date, date_field)
            elif start_date:
                # 只有开始日期，使用开始日期路由
                table_name = config.get_table_name(start_date)
                self._switch_table(table_name)
            elif end_date:
                # 只有结束日期，使用结束日期路由
                table_name = config.get_table_name(end_date)
                self._switch_table(table_name)
        elif f'{date_field}__range' in kwargs:
            # 范围查询：stat_date__range=[start, end]
            date_range = kwargs[f'{date_field}__range']
            if date_range and len(date_range) == 2:
                return self.filter_by_date_range(date_range[0], date_range[1], date_field)
        
        # 调用父类的 filter 方法
        return super().filter(*args, **kwargs)
    
    def filter_by_date(self, date_value, date_field: Optional[str] = None):
        """
        按日期过滤，自动路由到对应分表
        
        Args:
            date_value: 日期值
            date_field: 日期字段名（可选，使用配置中的默认字段）
            
        Returns:
            QuerySet: 查询集
        """
        config = self._get_shard_config()
        field_name = date_field or config.get_date_field()
        table_name = config.get_table_name(date_value)
        
        # 切换表名
        self._switch_table(table_name)
        
        # 应用过滤条件
        return self.filter(**{field_name: date_value})
    
    def filter_by_month(self, year: int, month: int):
        """
        按年月过滤
        
        Args:
            year: 年份
            month: 月份（1-12）
            
        Returns:
            QuerySet: 查询集
        """
        date_value = date(year, month, 1)
        return self.filter_by_date(date_value)
    
    def filter_by_year(self, year: int):
        """
        按年过滤
        
        Args:
            year: 年份
            
        Returns:
            QuerySet: 查询集
        """
        date_value = date(year, 1, 1)
        return self.filter_by_date(date_value)
    
    def filter_by_date_range(self, start_date, end_date, date_field: Optional[str] = None):
        """
        按日期范围过滤（跨分表查询）
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            date_field: 日期字段名
            
        Returns:
            QuerySet: 查询集（注意：跨表查询需要特殊处理）
        """
        config = self._get_shard_config()
        field_name = date_field or config.get_date_field()
        
        start_suffix = config.get_shard_suffix(start_date)
        end_suffix = config.get_shard_suffix(end_date)
        
        if start_suffix == end_suffix:
            # 同一个月，只查询一个表
            table_name = config.get_table_name(start_date)
            self._switch_table(table_name)
            return self.filter(**{
                f'{field_name}__gte': start_date,
                f'{field_name}__lte': end_date
            })
        else:
            # 跨月查询（简化处理：返回第一个表的查询集）
            # 实际应用中，应该查询多个表并合并结果
            logger.warning(f"跨分表查询: {start_suffix} -> {end_suffix}，仅查询第一个分表")
            table_name = config.get_table_name(start_date)
            self._switch_table(table_name)
            return self.filter(**{
                f'{field_name}__gte': start_date,
                f'{field_name}__lte': end_date
            })
    
    def _clone(self):
        """克隆查询集"""
        clone = super()._clone()
        clone._shard_table = self._shard_table
        clone._shard_config = self._shard_config
        return clone
    
    def iterator(self, chunk_size=2000):
        """迭代查询结果"""
        try:
            return super().iterator(chunk_size)
        finally:
            self._restore_table()
    
    def __iter__(self):
        """迭代器"""
        try:
            return super().__iter__()
        finally:
            self._restore_table()


class ShardingManager(Manager):
    """分表管理器"""
    
    def __init__(self):
        super().__init__()
        self._shard_config = None
    
    def _get_shard_config(self):
        """获取分表配置"""
        if self._shard_config is None:
            model = self.model
            sharding_config = getattr(model, 'sharding_config', None)
            self._shard_config = ShardingConfig(model, sharding_config)
        return self._shard_config
    
    def get_queryset(self):
        """获取查询集"""
        return ShardingQuerySet(self.model, using=self._db)
    
    def _ensure_table_exists(self, table_name: str):
        """
        确保分表存在
        
        Args:
            table_name: 表名
        """
        config = self._get_shard_config()
        
        if not config.config.get('auto_create_table', True):
            return
        
        with connection.cursor() as cursor:
            # 检查表是否存在（兼容PostgreSQL/Vastbase）
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_name = %s
            """, [table_name])
            
            exists = cursor.fetchone()[0] > 0
            
            if not exists:
                # 获取基础表名
                base_table = config.get_base_table()
                
                # 创建分表（复制表结构）
                # 注意：不同数据库语法可能不同，这里以PostgreSQL为例
                cursor.execute(f"""
                    CREATE TABLE {table_name} (LIKE {base_table} INCLUDING ALL)
                """)
                
                logger.info(f"自动创建分表: {table_name}")
    
    def create(self, **kwargs):
        """
        创建记录，自动路由到对应分表
        
        Args:
            **kwargs: 模型字段值
            
        Returns:
            模型实例
        """
        config = self._get_shard_config()
        date_field = config.get_date_field()
        
        # 获取日期字段值
        date_value = kwargs.get(date_field)
        if not date_value:
            # 如果没有日期字段，使用当前日期
            date_value = datetime.now().date()
            kwargs[date_field] = date_value
        
        # 获取分表名
        table_name = config.get_table_name(date_value)
        
        # 确保表存在
        self._ensure_table_exists(table_name)
        
        # 临时修改模型的表名
        original_table = self.model._meta.db_table
        self.model._meta.db_table = table_name
        
        try:
            # 创建记录
            instance = super().create(**kwargs)
            return instance
        finally:
            # 恢复原始表名
            self.model._meta.db_table = original_table
    
    def bulk_create(self, objs, batch_size=None, update_conflicts=True, update_fields=None, unique_fields=['id']):
        """
        批量创建记录，自动路由到对应分表
        参考 create 方法的实现：确认并创建分表，切换分表映射，再插入数据
        
        Args:
            objs: 模型实例列表
            batch_size: 批量插入大小
            update_conflicts: 是否更新冲突记录（默认True）
            update_fields: 更新字段列表（默认None，自动获取所有可更新字段）
            unique_fields: 唯一字段列表（默认['id']）
            
        Returns:
            List[模型实例]: 处理后的模型实例列表
                注意：当使用 update_conflicts=True 时，返回列表包含：
                - 新创建的记录
                - 更新的记录（也会在返回列表中）
                无法直接区分哪些是新创建的，哪些是更新的
        """
        if not objs:
            return []
        
        # 当 update_conflicts=True 且 update_fields=None 时，自动获取所有可更新字段
        if update_conflicts and update_fields is None:
            update_fields = self._get_updateable_fields(unique_fields)
        
        config = self._get_shard_config()
        date_field = config.get_date_field()
        
        # 按日期字段分组对象
        grouped_objects = defaultdict(list)
        for obj in objs:
            date_value = getattr(obj, date_field, None)
            if not date_value:
                # 如果没有日期字段，使用当前日期
                date_value = datetime.now().date()
                setattr(obj, date_field, date_value)
            grouped_objects[date_value].append(obj)
        
        # 保存原始表名
        original_table = self.model._meta.db_table
        
        all_processed = []
        
        try:
            # 对每个日期分组分别处理
            for date_value, date_objects in grouped_objects.items():
                # 获取分表名
                table_name = config.get_table_name(date_value)
                
                # 确保表存在
                self._ensure_table_exists(table_name)
                
                # 切换分表映射
                self.model._meta.db_table = table_name
                
                try:
                    # 批量插入数据
                    # 注意：bulk_create 返回的是处理后的对象列表
                    # 当使用 update_conflicts=True 时，返回列表包含新创建和更新的记录
                    # Django 不会区分哪些是新创建的，哪些是更新的
                    processed = super().bulk_create(
                        date_objects,
                        batch_size=batch_size,
                        update_conflicts=update_conflicts,
                        update_fields=update_fields,
                        unique_fields=unique_fields
                    )
                    all_processed.extend(processed)
                    logger.info(f"成功处理 {len(processed)} 条数据到分表 {table_name}（包含新创建和更新的记录）")
                except Exception as e:
                    logger.error(f"插入分表 {table_name} 失败: {str(e)}", exc_info=True)
                    raise
        finally:
            # 恢复原始表名
            self.model._meta.db_table = original_table
        
        return all_processed
    
    def _get_updateable_fields(self, unique_fields=None):
        """
        获取所有可更新的字段列表
        排除主键、唯一字段和审计字段
        
        Args:
            unique_fields: 唯一字段列表
            
        Returns:
            List[str]: 可更新字段列表
        """
        if unique_fields is None:
            unique_fields = ['id']
        
        # 获取所有字段
        all_fields = self.model._meta.get_fields()
        
        # 需要排除的字段
        exclude_fields = set(unique_fields)
        
        # 添加主键字段
        pk_field = self.model._meta.pk
        if pk_field:
            exclude_fields.add(pk_field.name)
        
        # 添加审计字段（通常不应该更新）
        audit_fields = ['create_datetime', 'creator', 'creator_id', 'creator_name']
        exclude_fields.update(audit_fields)
        
        # 获取可更新字段
        updateable_fields = []
        for field in all_fields:
            # 跳过关系字段
            if field.is_relation:
                continue
            
            # 跳过排除的字段
            if field.name in exclude_fields:
                continue
            
            # 跳过自动字段
            if hasattr(field, 'auto_now') and field.auto_now:
                continue
            if hasattr(field, 'auto_now_add') and field.auto_now_add:
                continue
            
            updateable_fields.append(field.name)
        
        return updateable_fields
    
    def filter_by_month(self, year: int, month: int):
        """
        按年月过滤
        
        Args:
            year: 年份
            month: 月份
            
        Returns:
            QuerySet
        """
        return self.get_queryset().filter_by_month(year, month)
    
    def filter_by_year(self, year: int):
        """
        按年过滤
        
        Args:
            year: 年份
            
        Returns:
            QuerySet
        """
        return self.get_queryset().filter_by_year(year)


class ShardingModelMixin:
    """
    分表模型 Mixin
    
    使用方法：
    class MyModel(ShardingModelMixin, BaseDataModel):
        sharding_config = {
            'date_field': 'stat_date',
            'shard_type': 'month',
            'base_table': 'my_table',
        }
        
        stat_date = models.DateField(...)
        objects = ShardingManager()
    """
    
    # 分表配置（子类可重写）
    sharding_config = None
    
    class Meta:
        abstract = True
    
    def __init_subclass__(cls, **kwargs):
        """子类初始化时设置管理器"""
        super().__init_subclass__(**kwargs)
        
        # 如果子类没有定义objects管理器，自动添加
        if not hasattr(cls, 'objects') or not isinstance(cls.objects, ShardingManager):
            cls.objects = ShardingManager()


class ShardingTableManager:
    """分表管理工具类"""
    
    def __init__(self, model_or_config):
        """
        初始化
        
        Args:
            model_or_config: Django模型类或ShardingConfig对象
        """
        if isinstance(model_or_config, ShardingConfig):
            self.config = model_or_config
        else:
            model = model_or_config
            sharding_config = getattr(model, 'sharding_config', None)
            self.config = ShardingConfig(model, sharding_config)
    
    def create_shard_table(self, date_value):
        """
        创建指定日期的分表
        
        Args:
            date_value: 日期值
            
        Returns:
            str: 操作结果消息
        """
        table_name = self.config.get_table_name(date_value)
        base_table = self.config.get_base_table()
        
        with connection.cursor() as cursor:
            # 检查表是否存在
            cursor.execute("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_name = %s
            """, [table_name])
            
            exists = cursor.fetchone()[0] > 0
            
            if exists:
                return f"分表 {table_name} 已存在"
            
            # 创建分表
            cursor.execute(f"""
                CREATE TABLE {table_name} (LIKE {base_table} INCLUDING ALL)
            """)
            
            return f"成功创建分表 {table_name}"
    
    def create_future_tables(self, months_ahead: int = 3):
        """
        预创建未来几个月的分表
        
        Args:
            months_ahead: 提前创建的月数
            
        Returns:
            list: 操作结果列表
        """
        from calendar import monthrange
        
        today = date.today()
        results = []
        
        for i in range(months_ahead):
            # 计算目标月份
            year = today.year
            month = today.month + i
            
            # 处理跨年
            while month > 12:
                month -= 12
                year += 1
            
            # 使用当月第一天作为日期
            target_date = date(year, month, 1)
            result = self.create_shard_table(target_date)
            results.append(result)
        
        return results
    
    def list_shard_tables(self) -> List[str]:
        """
        列出所有分表
        
        Returns:
            list: 分表名称列表
        """
        base_table = self.config.get_base_table()
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name LIKE %s
                ORDER BY table_name
            """, [f"{base_table}_%"])
            
            return [row[0] for row in cursor.fetchall()]
    
    def drop_shard_table(self, date_value):
        """
        删除指定日期的分表（谨慎使用）
        
        Args:
            date_value: 日期值
            
        Returns:
            str: 操作结果消息
        """
        table_name = self.config.get_table_name(date_value)
        
        with connection.cursor() as cursor:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            return f"已删除分表 {table_name}"
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        获取分表信息（记录数、大小等）
        
        Args:
            table_name: 表名
            
        Returns:
            dict: 表信息
        """
        with connection.cursor() as cursor:
            try:
                # 获取记录数
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                # 获取表大小（PostgreSQL语法）
                cursor.execute("""
                    SELECT pg_size_pretty(pg_total_relation_size(%s))
                """, [table_name])
                size_result = cursor.fetchone()
                table_size = size_result[0] if size_result else None
                
                return {
                    'table_name': table_name,
                    'row_count': row_count,
                    'table_size': table_size,
                }
            except Exception as e:
                return {
                    'table_name': table_name,
                    'row_count': None,
                    'table_size': None,
                    'error': str(e)
                }

