"""
数据权限扩展模块

提供自定义数据权限规则配置功能，扩展原框架的固定数据权限范围（0-4）。

功能特性：
- 自定义字段过滤规则
- 灵活的操作符（=, >, <, IN, LIKE等）
- 动态值类型（当前用户、当前部门、部门树等）
- 逻辑表达式组合（AND, OR, 括号）
- 可视化配置（前端支持）

使用方式：
1. 在角色权限配置中，选择 data_range=5（自定义规则）
2. 配置 custom_rules JSON
3. 系统自动应用规则引擎过滤数据
"""

default_app_config = 'dvadmin_extensions.data_permission.apps.DataPermissionConfig'

