"""
Vastbase数据库后端 - 基础包装器
基于Django的PostgreSQL后端，适配PostgreSQL 9.2.4
"""
from django.db.backends.postgresql import base
from .features import DatabaseFeatures
from .introspection import DatabaseIntrospection
from .operations import DatabaseOperations
from .schema import DatabaseSchemaEditor


class DatabaseWrapper(base.DatabaseWrapper):
    """
    Vastbase数据库包装器
    继承自PostgreSQL后端，针对PostgreSQL 9.2.4进行适配
    """
    vendor = 'vastbase'
    display_name = 'Vastbase'
    
    # 使用自定义的特性、内省和操作类
    features_class = DatabaseFeatures
    introspection_class = DatabaseIntrospection
    ops_class = DatabaseOperations
    schema_editor_class = DatabaseSchemaEditor

    # PostgreSQL 9.2 使用 SERIAL/BIGSERIAL 实现自增
    data_types = base.DatabaseWrapper.data_types.copy()
    data_types.update(
        {
            "AutoField": "serial",
            "BigAutoField": "bigserial",
            "SmallAutoField": "smallserial",
        }
    )
    data_types_suffix = {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 可以在这里添加额外的初始化逻辑
    
    def check_database_version_supported(self):
        """
        重写版本检查方法
        Vastbase基于PostgreSQL 9.2.4，跳过Django对PostgreSQL 12+的版本要求
        """
        # 获取数据库版本用于日志，但不做强制检查
        if self.connection is not None:
            version = self.pg_version
            # 记录版本信息但不抛出异常
            if version < 90204:  # 低于9.2.4才警告
                import warnings
                warnings.warn(
                    f'Vastbase版本 {version} 可能不完全兼容，建议使用9.2.4或更高版本',
                    RuntimeWarning
                )
    
    def get_database_version(self):
        """
        获取数据库版本
        返回数据库版本元组
        """
        if not self.connection:
            self.connect()
        return self.pg_version
    
    def init_connection_state(self):
        """
        初始化连接状态
        重写以确保版本检查不会失败
        """
        # 先获取版本信息
        cursor = self.connection.cursor()
        cursor.execute("SELECT version()")
        version_string = cursor.fetchone()[0]
        cursor.close()
        
        # 设置时区
        settings_dict = self.settings_dict
        if settings_dict.get('TIME_ZONE'):
            timezone = settings_dict['TIME_ZONE']
        else:
            timezone = 'UTC'
        
        cursor = self.connection.cursor()
        try:
            cursor.execute("SET TIME ZONE %s", [timezone])
        finally:
            cursor.close()
        
        # 设置连接参数
        if settings_dict.get('OPTIONS'):
            options = settings_dict['OPTIONS']
            if 'isolation_level' in options:
                self.connection.set_isolation_level(options['isolation_level'])
        
        # 调用父类方法但跳过版本检查
        # 不调用super().init_connection_state()因为它会调用check_database_version_supported
        # 我们已经在上面手动完成了必要的初始化

