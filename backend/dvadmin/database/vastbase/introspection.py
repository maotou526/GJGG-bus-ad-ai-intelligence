"""
Vastbase数据库内省模块
修复PostgreSQL 9.2.4与Django 4.2的兼容性问题
"""
from collections import namedtuple
from django.db.backends.postgresql.introspection import DatabaseIntrospection as PostgreSQLIntrospection

# 定义TableInfo命名元组
TableInfo = namedtuple('TableInfo', ['name', 'type'])


class DatabaseIntrospection(PostgreSQLIntrospection):
    """
    Vastbase数据库内省类
    重写部分方法以兼容PostgreSQL 9.2.4
    """
    
    def get_table_list(self, cursor):
        """
        获取数据库中的表列表
        移除对relispartition的查询（PostgreSQL 10+特性）
        """
        # PostgreSQL 9.2.4不支持分区表，简化查询
        cursor.execute("""
            SELECT
                c.relname,
                CASE
                    WHEN c.relkind = 'r' THEN 't'
                    WHEN c.relkind = 'v' THEN 'v'
                    WHEN c.relkind = 'm' THEN 'v'
                END AS rel_kind
            FROM pg_catalog.pg_class c
            LEFT JOIN pg_catalog.pg_namespace n ON n.oid = c.relnamespace
            WHERE c.relkind IN ('r', 'v', 'm')
                AND n.nspname NOT IN ('pg_catalog', 'pg_toast', 'information_schema')
                AND pg_catalog.pg_table_is_visible(c.oid)
        """)
        
        return [
            TableInfo(row[0], row[1])
            for row in cursor.fetchall()
            if row[1]
        ]
    
    def get_sequences(self, cursor, table_name, table_fields=()):
        """
        获取序列信息
        PostgreSQL 9.2兼容版本
        """
        # 简化序列查询
        cursor.execute("""
            SELECT s.relname as sequence_name, col.attname as column_name
            FROM pg_class s
            JOIN pg_depend d ON d.objid = s.oid AND d.classid = 'pg_class'::regclass
            JOIN pg_class t ON d.refobjid = t.oid
            JOIN pg_attribute col ON (d.refobjid, d.refobjsubid) = (col.attrelid, col.attnum)
            JOIN pg_namespace n ON n.oid = s.relnamespace
            WHERE s.relkind = 'S'
                AND t.relname = %s
                AND n.nspname NOT IN ('pg_catalog', 'pg_toast')
        """, [table_name])
        
        return [
            {'name': row[0], 'table': table_name, 'column': row[1]}
            for row in cursor.fetchall()
        ]
    
    def get_relations(self, cursor, table_name):
        """
        获取表的外键关系
        PostgreSQL 9.2兼容版本
        """
        cursor.execute("""
            SELECT c2.relname, a1.attname, a2.attname
            FROM pg_constraint con
            LEFT JOIN pg_class c1 ON con.conrelid = c1.oid
            LEFT JOIN pg_class c2 ON con.confrelid = c2.oid
            LEFT JOIN pg_attribute a1 ON c1.oid = a1.attrelid AND a1.attnum = con.conkey[1]
            LEFT JOIN pg_attribute a2 ON c2.oid = a2.attrelid AND a2.attnum = con.confkey[1]
            WHERE c1.relname = %s
                AND con.contype = 'f'
        """, [table_name])
        
        return {row[1]: (row[2], row[0]) for row in cursor.fetchall()}
    
    def get_key_columns(self, cursor, table_name):
        """
        获取表的主键和外键列信息
        PostgreSQL 9.2兼容版本
        """
        key_columns = []
        cursor.execute("""
            SELECT kcu.column_name, ccu.table_name AS referenced_table, ccu.column_name AS referenced_column
            FROM information_schema.constraint_column_usage ccu
            LEFT JOIN information_schema.key_column_usage kcu
                ON ccu.constraint_catalog = kcu.constraint_catalog
                AND ccu.constraint_schema = kcu.constraint_schema
                AND ccu.constraint_name = kcu.constraint_name
            LEFT JOIN information_schema.table_constraints tc
                ON ccu.constraint_catalog = tc.constraint_catalog
                AND ccu.constraint_schema = tc.constraint_schema
                AND ccu.constraint_name = tc.constraint_name
            WHERE kcu.table_name = %s AND tc.constraint_type = 'FOREIGN KEY'
        """, [table_name])
        
        key_columns.extend(cursor.fetchall())
        return key_columns
    
    def get_constraints(self, cursor, table_name):
        """
        获取表的约束信息
        简化版本，兼容PostgreSQL 9.2
        """
        constraints = {}
        
        # 获取主键和唯一约束
        cursor.execute("""
            SELECT
                c.conname,
                c.contype,
                array_agg(a.attname ORDER BY array_position(c.conkey, a.attnum))
            FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)
            WHERE t.relname = %s
                AND c.contype IN ('p', 'u', 'c')
            GROUP BY c.conname, c.contype
        """, [table_name])
        
        for constraint, kind, columns in cursor.fetchall():
            constraints[constraint] = {
                'columns': list(columns) if columns else [],
                'primary_key': kind == 'p',
                'unique': kind == 'u',
                'check': kind == 'c',
                'foreign_key': None,
                'index': False,
            }
        
        # 获取外键约束
        cursor.execute("""
            SELECT
                c.conname,
                array_agg(a.attname ORDER BY array_position(c.conkey, a.attnum)),
                t2.relname,
                array_agg(a2.attname ORDER BY array_position(c.confkey, a2.attnum))
            FROM pg_constraint c
            JOIN pg_class t ON c.conrelid = t.oid
            JOIN pg_class t2 ON c.confrelid = t2.oid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(c.conkey)
            JOIN pg_attribute a2 ON a2.attrelid = t2.oid AND a2.attnum = ANY(c.confkey)
            WHERE t.relname = %s
                AND c.contype = 'f'
            GROUP BY c.conname, t2.relname
        """, [table_name])
        
        for constraint, columns, ref_table, ref_columns in cursor.fetchall():
            constraints[constraint] = {
                'columns': list(columns) if columns else [],
                'primary_key': False,
                'unique': False,
                'check': False,
                'foreign_key': (ref_table, list(ref_columns)[0] if ref_columns else None),
                'index': False,
            }
        
        # 获取索引
        cursor.execute("""
            SELECT
                i.relname,
                array_agg(a.attname ORDER BY array_position(ix.indkey, a.attnum)),
                ix.indisunique,
                ix.indisprimary
            FROM pg_index ix
            JOIN pg_class t ON ix.indrelid = t.oid
            JOIN pg_class i ON ix.indexrelid = i.oid
            JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE t.relname = %s
                AND t.relkind = 'r'
            GROUP BY i.relname, ix.indisunique, ix.indisprimary
        """, [table_name])
        
        for index, columns, unique, primary in cursor.fetchall():
            if index not in constraints:
                constraints[index] = {
                    'columns': list(columns) if columns else [],
                    'primary_key': primary,
                    'unique': unique,
                    'check': False,
                    'foreign_key': None,
                    'index': True,
                }
        
        return constraints

