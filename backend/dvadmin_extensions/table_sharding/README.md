# 分表管理扩展模块

## 概述

提供统一的 Django 分表管理框架，支持在代码层面配置和管理分表，无需数据库记录。

## 功能特性

- ✅ **纯代码实现**：分表配置直接在模型代码中定义，无需数据库记录
- ✅ **自动路由**：根据日期字段自动路由到对应分表
- ✅ **自动创建**：首次写入时自动创建分表
- ✅ **灵活配置**：支持按年/月/日分表
- ✅ **API 管理**：提供完整的 REST API 管理分表
- ✅ **统一框架**：所有模型使用相同的分表框架

## 快速开始

### 1. 在模型中使用分表

```python
# backend/dvadmin_twodev/od/od_details/models.py
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_extensions.table_sharding.sharding import ShardingModelMixin, ShardingManager

class OdDetailsModel(ShardingModelMixin, BaseDataModel):
    """
    OD明细数据模型 - 支持自动分表
    """
    
    # 分表配置
    sharding_config = {
        'date_field': 'stat_date',      # 使用班次日期分表
        'shard_type': 'month',          # 按月分表
        'base_table': 'od_details',     # 基础表名
        'auto_create_table': True,       # 自动创建分表
    }
    
    # 使用分表管理器
    objects = ShardingManager()
    
    # 字段定义
    stat_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="班次日期",
        help_text="班次日期",
        db_comment="班次日期"
    )
    
    # ... 其他字段 ...
    
    class Meta:
        db_table = 'od_details'
        verbose_name = "OD明细数据"
        verbose_name_plural = "OD明细数据"
```

### 2. 使用分表进行数据操作

```python
from datetime import date
from dvadmin_twodev.od.od_details.models import OdDetailsModel

# 创建数据（自动路由到对应分表）
OdDetailsModel.objects.create(
    stat_date=date(2025, 1, 15),
    line_name="1路",
    # ... 其他字段
)

# 按月份查询
queryset = OdDetailsModel.objects.filter_by_month(2025, 1).all()

# 按日期查询（自动路由）
queryset = OdDetailsModel.objects.filter_by_date(date(2025, 1, 15)).all()

# 按年查询
queryset = OdDetailsModel.objects.filter_by_year(2025).all()
```

## API 接口

### 1. 列出所有配置了分表的模型

```http
GET /api/ext/table_sharding/list-models/
```

**响应示例：**
```json
{
    "code": 2000,
    "data": [
        {
            "model_name": "dvadmin_twodev.od.od_details.models.OdDetailsModel",
            "app_label": "od_details",
            "base_table": "od_details",
            "date_field": "stat_date",
            "shard_type": "month",
            "auto_create": true
        }
    ],
    "msg": "获取成功"
}
```

### 2. 列出指定模型的所有分表

```http
GET /api/ext/table_sharding/list-shard-tables/?model_name=dvadmin_twodev.od.od_details.models.OdDetailsModel
```

**响应示例：**
```json
{
    "code": 2000,
    "data": [
        {
            "table_name": "od_details_202501",
            "row_count": 10000,
            "table_size": "2.5 MB"
        },
        {
            "table_name": "od_details_202502",
            "row_count": 15000,
            "table_size": "3.8 MB"
        }
    ],
    "msg": "获取成功"
}
```

### 3. 创建分表

**创建单个分表：**
```http
POST /api/ext/table_sharding/create-shard-table/
Content-Type: application/json

{
    "model_name": "dvadmin_twodev.od.od_details.models.OdDetailsModel",
    "date": "2025-03-01"
}
```

**批量创建未来几个月的分表：**
```http
POST /api/ext/table_sharding/create-shard-table/
Content-Type: application/json

{
    "model_name": "dvadmin_twodev.od.od_details.models.OdDetailsModel",
    "months_ahead": 3
}
```

### 4. 删除分表（谨慎使用）

```http
POST /api/ext/table_sharding/drop-shard-table/
Content-Type: application/json

{
    "model_name": "dvadmin_twodev.od.od_details.models.OdDetailsModel",
    "date": "2025-01-01"
}
```

### 5. 获取分表详细信息

```http
GET /api/ext/table_sharding/table-info/?model_name=dvadmin_twodev.od.od_details.models.OdDetailsModel&date=2025-01-01
```

## 配置说明

### sharding_config 配置项

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `date_field` | str | `'create_datetime'` | 用于分表的日期字段名 |
| `shard_type` | str | `'month'` | 分表粒度：`year`/`month`/`day` |
| `base_table` | str | 模型 Meta.db_table | 基础表名 |
| `auto_create_table` | bool | `True` | 是否自动创建分表 |

### 分表类型说明

- **year**：按年分表，表名格式：`table_2025`
- **month**：按月分表，表名格式：`table_202501`
- **day**：按日分表，表名格式：`table_20250115`

## 使用示例

### 示例1：OD明细数据按月分表

```python
class OdDetailsModel(ShardingModelMixin, BaseDataModel):
    sharding_config = {
        'date_field': 'stat_date',
        'shard_type': 'month',
        'base_table': 'od_details',
    }
    objects = ShardingManager()
    
    stat_date = models.DateField(...)
```

### 示例2：日志数据按日分表

```python
class LogModel(ShardingModelMixin, BaseDataModel):
    sharding_config = {
        'date_field': 'create_datetime',
        'shard_type': 'day',
        'base_table': 'system_log',
    }
    objects = ShardingManager()
    
    create_datetime = models.DateTimeField(...)
```

### 示例3：年度报表按年分表

```python
class AnnualReportModel(ShardingModelMixin, BaseDataModel):
    sharding_config = {
        'date_field': 'report_year',
        'shard_type': 'year',
        'base_table': 'annual_report',
    }
    objects = ShardingManager()
    
    report_year = models.DateField(...)
```

## 注意事项

1. **跨分表查询**：当前版本跨分表查询仅返回第一个分表的结果，建议限制查询范围在一个分表内
2. **表名格式**：分表名格式为 `{base_table}_{suffix}`，suffix 根据分表类型自动生成
3. **自动创建**：首次写入数据时会自动创建对应的分表，确保基础表已存在
4. **数据库兼容性**：当前实现基于 PostgreSQL/Vastbase，其他数据库可能需要调整 SQL 语法

## 文件结构

```
backend/dvadmin_extensions/table_sharding/
├── __init__.py          # 模块初始化
├── apps.py              # 应用配置
├── sharding.py          # 分表核心工具类
├── serializers.py       # API序列化器
├── views.py             # API视图集
├── urls.py              # 路由配置
└── README.md            # 本文档
```

## 核心类说明

- **ShardingConfig**：分表配置类，解析和验证分表配置
- **ShardingQuerySet**：分表查询集，支持按日期/月份/年份查询
- **ShardingManager**：分表管理器，自动路由到对应分表
- **ShardingModelMixin**：分表模型 Mixin，提供分表能力
- **ShardingTableManager**：分表管理工具类，提供创建/删除/查询分表功能

## 扩展开发

如果需要扩展分表功能，可以：

1. 继承 `ShardingConfig` 添加自定义分表策略
2. 重写 `ShardingManager.create()` 实现自定义创建逻辑
3. 在 `views.py` 中添加新的 API 接口

## 常见问题

### Q1: 如何查看某个模型是否配置了分表？

A: 调用 API `GET /api/ext/table_sharding/list-models/` 查看所有配置了分表的模型。

### Q2: 如何手动创建分表？

A: 调用 API `POST /api/ext/table_sharding/create-shard-table/` 或使用代码：
```python
from dvadmin_extensions.table_sharding.sharding import ShardingTableManager
from datetime import date

manager = ShardingTableManager(OdDetailsModel)
manager.create_shard_table(date(2025, 1, 1))
```

### Q3: 分表数据如何查询？

A: 使用分表管理器的方法：
```python
# 按月份查询
OdDetailsModel.objects.filter_by_month(2025, 1).all()

# 按日期查询
OdDetailsModel.objects.filter_by_date(date(2025, 1, 15)).all()
```

### Q4: 如何删除旧的分表？

A: 调用 API `POST /api/ext/table_sharding/drop-shard-table/` 或使用代码：
```python
manager.drop_shard_table(date(2025, 1, 1))
```

## 更新日志

### v1.0.0 (2025-11-26)
- 初始版本
- 支持按年/月/日分表
- 提供完整的 REST API
- 纯代码实现，无需数据库记录

