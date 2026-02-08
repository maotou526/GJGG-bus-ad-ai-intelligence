'''
Description: 分表过滤器
Version: 1.0
Author: 王晨
Date: 2025-11-26
LastEditors: 王晨
LastEditTime: 2025-11-26 11:15:01
'''
from datetime import datetime, date
from rest_framework.filters import BaseFilterBackend
from .sharding import ShardingConfig
import logging

logger = logging.getLogger(__name__)


class ShardingTableFilter(BaseFilterBackend):
    """
    分表过滤器
    
    功能：
    1. 在查询前检测查询参数中的日期字段（如 stat_date）
    2. 根据日期值自动路由到对应的分表
    3. 支持精确查询和范围查询
    
    优先级：
    - 应该在所有其他过滤器之前执行（最高优先级）
    - 在 extra_filter_class 中排第一位
    """
    
    def filter_queryset(self, request, queryset, view):
        """
        检测日期参数并路由到对应分表
        
        Args:
            request: Django Request 对象
            queryset: Django QuerySet 对象
            view: 视图对象
        
        Returns:
            QuerySet: 已路由到对应分表的查询集
        """
        # 检查模型是否配置了分表
        model = queryset.model
        if not hasattr(model, 'sharding_config') or not model.sharding_config:
            # 模型未配置分表，跳过
            return queryset
        
        try:
            config = ShardingConfig(model, model.sharding_config)
            date_field = config.get_date_field()
            
            # 从查询参数中获取日期值
            date_value = self._extract_date_from_params(request, date_field)
            
            # 确定要使用的表名
            table_name = None
            
            if date_value:
                # 有日期参数，路由到对应分表
                table_name = config.get_table_name(date_value)
                logger.debug(f"分表路由: {model.__name__} -> {table_name} (date={date_value})")
            else:
                # 没有日期参数，检查是否有范围查询
                start_date, end_date = self._extract_date_range_from_params(request, date_field)
                
                if start_date and end_date:
                    # 有日期范围，路由到对应的分表
                    start_suffix = config.get_shard_suffix(start_date)
                    end_suffix = config.get_shard_suffix(end_date)
                    
                    if start_suffix == end_suffix:
                        # 同一天，路由到对应分表
                        table_name = config.get_table_name(start_date)
                        logger.debug(f"分表路由: {model.__name__} -> {table_name} (range={start_date} to {end_date})")
                    else:
                        # 跨天查询，路由到第一个分表（简化处理）
                        table_name = config.get_table_name(start_date)
                        logger.warning(f"跨分表查询: {start_suffix} -> {end_suffix}，仅查询第一个分表 {table_name}")
                elif start_date:
                    # 只有开始日期
                    table_name = config.get_table_name(start_date)
                    logger.debug(f"分表路由: {model.__name__} -> {table_name} (start_date={start_date})")
                elif end_date:
                    # 只有结束日期
                    table_name = config.get_table_name(end_date)
                    logger.debug(f"分表路由: {model.__name__} -> {table_name} (end_date={end_date})")
                else:
                    # 没有日期参数，保持原表名（基础表）
                    # 注意：这种情况下可能查询不到数据，因为数据都在分表中
                    logger.warning(f"分表模型 {model.__name__} 查询时未提供日期参数，可能查询不到数据")
                    return queryset
            
            # 如果有表名，需要切换表名
            if table_name:
                # 检查表是否存在
                table_exists = self._check_table_exists(table_name)
                logger.debug(f"检查表 {table_name} 是否存在: {table_exists}")
                
                if not table_exists:
                    # 表不存在，在 request 上设置标记，供后续处理
                    request._sharding_table_not_exists = {
                        'table_name': table_name,
                        'date_value': date_value or (start_date if start_date else end_date),
                        'date_field': date_field
                    }
                    logger.warning(f"分表不存在: {table_name}")
                    # 返回空查询集，避免查询原表
                    return model.objects.none()
                # 表存在则交给 ShardingQuerySet 处理，不直接修改 QuerySet
            
            return queryset
            
        except Exception as e:
            logger.error(f"分表路由失败: {e}", exc_info=True)
            # 出错时返回原查询集，保证系统可用性
            return queryset
    
    def _extract_date_from_params(self, request, date_field: str):
        """
        从查询参数中提取日期值
        
        Args:
            request: Django Request 对象
            date_field: 日期字段名
            
        Returns:
            date 对象或 None
        """
        # 检查精确匹配
        date_str = request.query_params.get(date_field)
        if date_str:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    return datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').date()
                except ValueError:
                    logger.warning(f"无法解析日期格式: {date_str}")
                    return None
        
        # 检查 __exact 查询
        date_str = request.query_params.get(f'{date_field}__exact')
        if date_str:
            try:
                return datetime.strptime(date_str, '%Y-%m-%d').date()
            except ValueError:
                return None
        
        return None
    
    def _extract_date_range_from_params(self, request, date_field: str):
        """
        从查询参数中提取日期范围
        
        Args:
            request: Django Request 对象
            date_field: 日期字段名
            
        Returns:
            tuple: (start_date, end_date) 或 (None, None)
        """
        start_date = None
        end_date = None
        
        # 检查 __gte 和 __lte
        start_str = request.query_params.get(f'{date_field}__gte')
        end_str = request.query_params.get(f'{date_field}__lte')
        
        if start_str:
            try:
                start_date = datetime.strptime(start_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    start_date = datetime.strptime(start_str, '%Y-%m-%d %H:%M:%S').date()
                except ValueError:
                    pass
        
        if end_str:
            try:
                end_date = datetime.strptime(end_str, '%Y-%m-%d').date()
            except ValueError:
                try:
                    end_date = datetime.strptime(end_str, '%Y-%m-%d %H:%M:%S').date()
                except ValueError:
                    pass
        
        # 检查 __range
        if not start_date or not end_date:
            range_str = request.query_params.get(f'{date_field}__range')
            if range_str:
                # 可能是逗号分隔的字符串，如 "2025-01-15,2025-01-20"
                try:
                    parts = range_str.split(',')
                    if len(parts) == 2:
                        start_date = datetime.strptime(parts[0].strip(), '%Y-%m-%d').date()
                        end_date = datetime.strptime(parts[1].strip(), '%Y-%m-%d').date()
                except (ValueError, IndexError):
                    pass
        
        return start_date, end_date
    
    def _check_table_exists(self, table_name: str) -> bool:
        """
        检查表是否存在
        
        Args:
            table_name: 表名
            
        Returns:
            bool: 表是否存在
        """
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                # 方法1：使用 information_schema（需要考虑 schema）
                # 获取当前 schema（通常是 'public'）
                cursor.execute("SELECT current_schema()")
                schema = cursor.fetchone()[0] or 'public'
                
                # 检查表是否存在（兼容PostgreSQL/Vastbase）
                # table_name 在 information_schema 中是小写的
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = %s 
                    AND LOWER(table_name) = LOWER(%s)
                """, [schema, table_name])
                
                exists = cursor.fetchone()[0] > 0
                
                if exists:
                    return True
                
                # 方法2：如果方法1没找到，尝试使用 pg_catalog（更可靠）
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM pg_catalog.pg_class c
                    JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
                    WHERE n.nspname = %s 
                    AND c.relname = %s
                    AND c.relkind = 'r'
                """, [schema, table_name])
                
                exists = cursor.fetchone()[0] > 0
                return exists
                
        except Exception as e:
            logger.error(f"检查表是否存在失败: {e}", exc_info=True)
            # 出错时返回 False，这样会触发友好错误提示
            return False

