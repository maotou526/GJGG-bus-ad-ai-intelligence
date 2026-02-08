"""
Vastbase数据库特性模块
定义PostgreSQL 9.2.4支持的特性
"""
from django.db.backends.postgresql.features import DatabaseFeatures as PostgreSQLFeatures


class DatabaseFeatures(PostgreSQLFeatures):
    """
    Vastbase数据库特性类
    针对PostgreSQL 9.2.4调整特性支持
    """
    
    # PostgreSQL 9.2.4不支持的特性
    has_select_for_update_of = False  # PostgreSQL 9.5+
    has_select_for_no_key_update = False  # PostgreSQL 9.5+
    supports_table_check_constraints = True
    can_defer_constraint_checks = True
    has_real_datatype = True
    has_native_uuid_field = True
    has_native_duration_field = True
    can_distinct_on_fields = True
    supports_temporal_subtraction = True
    supports_regex_backreferencing = True
    supports_date_lookup_using_string = False
    supports_timezones = True
    
    # PostgreSQL 10+特性，9.2.4不支持
    supports_table_partitions = False
    can_introspect_materialized_views = True  # PostgreSQL 9.3+，但9.2也有物化视图概念
    
    # JSONB是PostgreSQL 9.4+特性，9.2只有JSON
    has_jsonb_datatype = False
    has_json_operators = False
    
    # 其他9.2不支持的特性
    supports_combined_alters = False
    supports_ignore_conflicts = False  # INSERT ... ON CONFLICT (PostgreSQL 9.5+)
    supports_partial_indexes = True
    supports_functions_in_partial_indexes = True
    supports_covering_indexes = False  # PostgreSQL 11+
    supports_expression_indexes = True
    can_rollback_ddl = True
    
    # 聚合函数支持
    supports_stddev = True
    supports_variance = True
    
    # 序列支持
    supports_sequence_reset = True
    
    # 事务特性
    can_release_savepoints = True
    supports_transactions = True
    uses_savepoints = True
    atomic_transactions = True
    
    # 其他配置
    requires_literal_defaults = False
    nulls_order_largest = False
    closed_cursor_error_class = None
    bare_select_suffix = ""
    allows_group_by_selected_pks = True
    allows_group_by_refs = True
    
    # 正则表达式支持
    supports_regex_backreferencing = True
    
    @property
    def is_postgresql_9(self):
        """标识为PostgreSQL 9.x"""
        return True
    
    @property
    def is_postgresql_10(self):
        """不是PostgreSQL 10+"""
        return False

