"""
分表管理扩展模块

提供统一的分表管理功能，支持：
- 自动分表（按时间、按业务字段）
- 分表创建和管理
- 分表查询路由
- 分表监控和统计

使用方式：
1. 在模型中继承 ShardingModelMixin 并配置 sharding_config
2. 使用 ShardingManager 进行数据操作
3. 通过 API 管理分表（创建、查询、删除）
"""

default_app_config = 'dvadmin_extensions.table_sharding.apps.TableShardingConfig'

