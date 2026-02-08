"""
达梦(Dameng)数据库后端
支持达梦数据库8.0及以上版本

依赖：
    pip install dmPython

使用方式：
    在 settings.py 的 DATABASES 配置中设置：
    DATABASES = {
        'dm': {
            'ENGINE': 'dvadmin.database.dm',
            'NAME': 'DAMENG',
            'USER': 'SYSDBA',
            'PASSWORD': 'SYSDBA',
            'HOST': '127.0.0.1',
            'PORT': 5236,
        }
    }
"""
from .base import DatabaseWrapper

__all__ = ['DatabaseWrapper']

