"""
Vastbase数据库操作模块
针对PostgreSQL 9.2.4的数据库操作
"""
from django.db.backends.postgresql.operations import DatabaseOperations as PostgreSQLOperations


class DatabaseOperations(PostgreSQLOperations):
    """
    Vastbase数据库操作类
    继承PostgreSQL操作，针对9.2.4进行适配
    """
    
    # compiler_module = "django.db.backends.postgresql.compiler"
    
    def __init__(self, connection):
        super().__init__(connection)
        # 可以在这里添加自定义初始化
    
    def sequence_reset_sql(self, style, model_list):
        """
        生成序列重置SQL
        兼容PostgreSQL 9.2
        """
        from django.db import models
        output = []
        qn = self.quote_name
        for model in model_list:
            # 获取模型的所有自增字段
            for f in model._meta.local_fields:
                if isinstance(f, models.AutoField):
                    tablename = model._meta.db_table
                    column = f.column
                    # 获取序列名
                    serial = f"{tablename}_{column}_seq"
                    output.append(
                        f"{style.SQL_KEYWORD('SELECT')}"
                        f" {style.SQL_KEYWORD('setval')}("
                        f"{style.SQL_FIELD(self.quote_name(serial))},"
                        f" {style.SQL_KEYWORD('COALESCE')}("
                        f"{style.SQL_KEYWORD('MAX')}({style.SQL_FIELD(qn(column))}), 1)"
                        f" {style.SQL_KEYWORD('FROM')} {style.SQL_TABLE(qn(tablename))});"
                    )
        return output
    
    def tablespace_sql(self, tablespace, inline=False):
        """
        生成表空间SQL
        """
        if inline:
            return "USING INDEX TABLESPACE %s" % self.quote_name(tablespace)
        else:
            return "TABLESPACE %s" % self.quote_name(tablespace)
    
    def prep_for_iexact_query(self, x):
        """
        为不区分大小写的查询准备值
        """
        return x
    
    def max_name_length(self):
        """
        PostgreSQL标识符最大长度为63
        """
        return 63
    
    def distinct_sql(self, fields, params):
        """
        生成DISTINCT SQL
        """
        if fields:
            params = [param for param_list in params for param in param_list]
            return (['DISTINCT ON (%s)' % ', '.join(fields)], params)
        else:
            return ['DISTINCT'], []
    
    def last_executed_query(self, cursor, sql, params):
        """
        返回最后执行的查询
        """
        # 使用psycopg2的mogrify方法
        try:
            return cursor.mogrify(sql, params).decode()
        except Exception:
            return super().last_executed_query(cursor, sql, params)
    
    def return_insert_columns(self, fields):
        """
        INSERT语句返回字段
        """
        if not fields:
            return '', ()
        columns = [
            '%s.%s' % (
                self.quote_name(field.model._meta.db_table),
                self.quote_name(field.column),
            ) for field in fields
        ]
        return 'RETURNING %s' % ', '.join(columns), ()
    
    def bulk_insert_sql(self, fields, placeholder_rows):
        """
        批量插入SQL
        兼容PostgreSQL 9.2
        """
        placeholder_rows_sql = (", ".join(row) for row in placeholder_rows)
        values_sql = ", ".join("(%s)" % sql for sql in placeholder_rows_sql)
        return "VALUES " + values_sql
    
    def adapt_datefield_value(self, value):
        """
        适配日期字段值
        """
        return value
    
    def adapt_datetimefield_value(self, value):
        """
        适配日期时间字段值
        """
        return value
    
    def adapt_timefield_value(self, value):
        """
        适配时间字段值
        """
        return value
    
    def adapt_decimalfield_value(self, value, max_digits=None, decimal_places=None):
        """
        适配小数字段值
        """
        return value
    
    def adapt_ipaddressfield_value(self, value):
        """
        适配IP地址字段值
        """
        if value:
            return str(value)
        return None

