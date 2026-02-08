# 达梦数据库 (DM Database) 集成指南

## 📋 目录

- [概述](#概述)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [数据库路由](#数据库路由)
- [Schema 管理](#schema-管理)
- [迁移管理](#迁移管理)
- [常见问题](#常见问题)
- [最佳实践](#最佳实践)

---

## 概述

本项目集成了达梦数据库（DM Database）作为辅助数据库，与默认的 Vastbase 数据库并存。通过 Django 的多数据库路由机制，可以灵活地将不同的应用模块路由到不同的数据库。

### 特性

- ✅ 多数据库支持（Vastbase + 达梦）
- ✅ 自动数据库路由
- ✅ Schema 自动切换
- ✅ 跨数据库软关联（审计字段）
- ✅ 独立迁移管理

### 架构图

```
┌─────────────────────────────────────────────────────┐
│                   Django Application                │
├─────────────────────────────────────────────────────┤
│              Database Router (db_router.py)         │
├──────────────────────┬──────────────────────────────┤
│   Default Database   │      DM Database             │
│   (Vastbase)         │      (达梦)                   │
├──────────────────────┼──────────────────────────────┤
│ • system (用户)      │ • park (停车场)               │
│ • auth (认证)        │ • vehicle (车辆)              │
│ • sessions           │ • roadline (线路)             │
│ • ...                │ • ...                         │
└──────────────────────┴──────────────────────────────┘
```

---

## 快速开始

### 1. 环境准备

#### 安装 dmPython 驱动

```bash
pip install dmPython
```

#### 验证安装

```bash
python -c "import dmPython; print('✅ dmPython 已安装')"
```

### 2. 数据库配置

在 `backend/application/settings.py` 中已配置：

```python
DATABASES = {
    "default": {
        "ENGINE": "dvadmin.database.vastbase",
        "NAME": "vastbase",
        "USER": "tpcc",
        "PASSWORD": "www.71AD.comTc",
        "HOST": "10.60.9.69",
        "PORT": 5432,
    },
    "dm": {
        "ENGINE": "dvadmin.database.dm",
        "NAME": "mhgj_dc",  # Schema 名称
        "USER": "SYSDBA",
        "PASSWORD": "wwW.71Ad.com",
        "HOST": "10.60.33.192",
        "PORT": 5236,
        "OPTIONS": {},
    }
}

# 数据库路由器
DATABASE_ROUTERS = ['dvadmin.utils.db_router.DatabaseRouter']
```

### 3. 配置路由

有两种方式可以将模型路由到达梦数据库：

#### 方式1：在路由器中配置（适用于整个应用）

在 `backend/dvadmin/utils/db_router.py` 中配置应用路由：

```python
class DatabaseRouter:
    app_db_map = {
        # 将 park 模块路由到达梦数据库
        'park': 'dm',
        
        # 添加其他需要路由的模块
        # 'vehicle': 'dm',
        # 'roadline': 'dm',
    }
```

**⚠️ 重要说明**：

- **使用 `app_label` 而不是完整路径**
- `app_label` 是 `apps.py` 中 `name` 的**最后一部分**
- 例如：`'dvadmin_twodev.basedata.park'` 的 `app_label` 是 `'park'`

#### 方式2：在模型中设置 db_label（推荐，适用于单个模型）

在 `apps.py` 的 `ready()` 方法中设置（详见下方"数据库路由"章节的详细说明）：

```python
# apps.py
def ready(self):
    from .models import YourModel
    YourModel._meta.db_label = "dm"
```

**优先级**：`db_label` > `app_db_map` > `default`

### 4. 执行迁移

```bash
# 在达梦数据库创建表
python manage.py migrate park --database=dm

# 查看迁移状态
python manage.py showmigrations park --database=dm
```

### 5. 验证配置

创建测试脚本 `test_dm.py`：

```python
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from dvadmin_twodev.basedata.park.models import ParkModel
from dvadmin.utils.db_router import DatabaseRouter

router = DatabaseRouter()
db = router.db_for_read(ParkModel)

print(f"✅ ParkModel 路由到数据库: {db}")
print(f"📊 记录数: {ParkModel.objects.count()}")
```

运行：
```bash
python test_dm.py
```

---

## 配置说明

### 数据库连接参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `ENGINE` | 数据库引擎 | `dvadmin.database.dm` |
| `NAME` | Schema 名称 | `mhgj_dc` |
| `USER` | 数据库用户 | `SYSDBA` |
| `PASSWORD` | 数据库密码 | `wwW.71Ad.com` |
| `HOST` | 数据库地址 | `10.60.33.192` |
| `PORT` | 数据库端口 | `5236` |
| `OPTIONS` | 额外选项 | `{}` |

### Schema 自动切换

连接建立后，系统会自动执行：

```sql
ALTER SESSION SET CURRENT_SCHEMA = MHGJ_DC
```

这确保所有操作都在指定的 Schema 下进行。

### 连接池配置（可选）

如需配置连接池，修改 `OPTIONS`：

```python
"OPTIONS": {
    "min_pool_size": 2,
    "max_pool_size": 10,
    "timeout": 30,
}
```

---

## 数据库路由

### 路由器工作原理

```python
class DatabaseRouter:
    """
    数据库路由器
    
    工作流程：
    1. 检查模型是否有 db_label 属性（最高优先级）
    2. 检查 app_label 是否在 app_db_map 中
    3. 默认使用 default 数据库
    """
    
    app_db_map = {
        'park': 'dm',
    }
    
    def db_for_read(self, model, **hints):
        """读操作路由"""
        # 1. 检查 db_label
        if hasattr(model._meta, "db_label"):
            return model._meta.db_label
        
        # 2. 检查 app_label
        app_label = model._meta.app_label
        if app_label in self.app_db_map:
            return self.app_db_map[app_label]
        
        # 3. 默认数据库
        return "default"
    
    def db_for_write(self, model, **hints):
        """写操作路由（同读操作）"""
        return self.db_for_read(model, **hints)
```

### app_label 的来源

Django 自动从 `apps.py` 中的 `name` 提取：

```python
# backend/dvadmin_twodev/basedata/park/apps.py
class ParkConfig(AppConfig):
    name = "dvadmin_twodev.basedata.park"
    # ↓ Django 自动提取
    # app_label = "park"
```

**验证方法**：

```python
from dvadmin_twodev.basedata.park.models import ParkModel

print(ParkModel._meta.app_config.name)   # 完整路径
# 输出: 'dvadmin_twodev.basedata.park'

print(ParkModel._meta.app_label)         # app_label
# 输出: 'park'
```

### 配置多个应用

```python
app_db_map = {
    # 基础数据模块
    'park': 'dm',
    'vehicle': 'dm',
    'roadline': 'dm',
    
    # OD 数据模块
    'od_details': 'dm',
    'od_device': 'dm',
    
    # OSM 数据模块
    'osm_node': 'dm',
    'osm_way': 'dm',
}
```

### 方式2：在模型中设置 db_label（推荐，最高优先级）

**⚠️ 重要说明**：Django 的 `Meta` 类不支持 `db_label` 属性，需要通过 `apps.py` 的 `ready()` 方法动态设置。

#### 实现步骤

1. **在 `apps.py` 中添加 `ready()` 方法**：

```python
# backend/dvadmin_twodev/basedata/test_demo/apps.py
from django.apps import AppConfig

class TestDemoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dvadmin_twodev.basedata.test_demo"
    verbose_name = "测试演示"
    
    def ready(self):
        """应用准备就绪时设置模型的 db_label"""
        from .models import DcBaseTorusinfoModel
        # 在应用完全初始化后设置 db_label
        DcBaseTorusinfoModel._meta.db_label = "dm"
```

2. **模型定义**（不需要在 Meta 中设置）：

```python
# backend/dvadmin_twodev/basedata/test_demo/models.py
from django.db import models

class DcBaseTorusinfoModel(models.Model):
    """环域信息模型"""
    
    id = models.CharField(max_length=50, primary_key=True, db_column="F_Id")
    # ... 其他字段 ...
    
    class Meta:
        db_table = "dc_base_torusinfo"
        verbose_name = "环域信息"
        managed = False
        # ⚠️ 注意：不要在这里设置 db_label，Django 不支持
```

#### 优势

- ✅ **最高优先级**：`db_label` 的优先级高于 `app_db_map` 配置
- ✅ **精确控制**：只影响当前模型，不影响整个应用
- ✅ **灵活性强**：同一个应用的不同模型可以使用不同数据库
- ✅ **无需修改路由器**：不需要在 `db_router.py` 中配置

#### 工作原理

- `ready()` 方法在 Django 应用完全初始化后调用
- 此时模型的 `_meta` 对象已完全创建，可以安全地设置属性
- 路由器在 `db_for_read()` 和 `db_for_write()` 中会优先检查 `model._meta.db_label`

#### 注意事项

- ⚠️ **必须在 `ready()` 方法中设置**：不能在模型定义时直接设置，因为 `_meta` 对象还未完全初始化
- ⚠️ **不能放在 Meta 类中**：Django 的 `Meta` 类不支持 `db_label` 属性，会报错 `TypeError: 'class Meta' got invalid attribute(s): db_label`
- ✅ **推荐用于单个模型路由**：如果整个应用都需要路由，使用 `app_db_map` 更简单

### 跨数据库关联

**问题**：`ParkModel` 在 DM 数据库，但 `creator` 字段关联到 `Users`（在 default 数据库）。

**解决**：路由器允许 `Users` 的跨数据库软关联：

```python
def allow_relation(self, obj1, obj2, **hints):
    """
    允许跨数据库的软关联
    
    CoreModel 中的审计字段（creator、modifier）使用
    db_constraint=False，不在数据库层面建立外键约束
    """
    db1 = self.db_for_read(obj1.__class__)
    db2 = self.db_for_read(obj2.__class__)
    
    if db1 == db2:
        return True
    
    # 允许 Users 的跨数据库关联（审计字段）
    from dvadmin.system.models import Users
    if obj1.__class__ == Users or obj2.__class__ == Users:
        return True
    
    return False
```

---

## Schema 管理

### 查询当前 Schema

```sql
SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL;
```

### 查询表所在 Schema

```sql
SELECT owner, table_name 
FROM ALL_TABLES 
WHERE table_name = 'DWD_PARK';
```

### 手动切换 Schema

```sql
ALTER SESSION SET CURRENT_SCHEMA = MHGJ_DC;
```

### 跨 Schema 访问

```sql
-- 访问其他 Schema 的表
SELECT * FROM SYSDBA.DWD_PARK;

-- 创建同义词
CREATE SYNONYM DWD_PARK FOR MHGJ_DC.DWD_PARK;
```

---

## 迁移管理

### 创建迁移

```bash
# 为 park 应用创建迁移
python manage.py makemigrations park
```

### 执行迁移

```bash
# 在达梦数据库执行迁移
python manage.py migrate park --database=dm

# 在默认数据库执行迁移
python manage.py migrate park
```

### 查看迁移状态

```bash
# 查看达梦数据库的迁移状态
python manage.py showmigrations park --database=dm

# 查看所有数据库的迁移状态
python manage.py showmigrations --database=dm
```

### 回滚迁移

```bash
# 回滚到初始状态
python manage.py migrate park zero --database=dm

# 回滚到指定迁移
python manage.py migrate park 0002 --database=dm
```

### 迁移路由控制

路由器的 `allow_migrate` 方法控制迁移在哪个数据库执行：

```python
def allow_migrate(self, db, app_label, model_name=None, **hints):
    """
    控制迁移执行位置
    
    规则：
    1. app_db_map 中的应用只在指定数据库迁移
    2. 核心应用（system、auth等）只在 default 迁移
    3. 其他应用默认在 default 迁移
    """
    # park 应用只在 dm 数据库迁移
    if app_label in self.app_db_map:
        return db == self.app_db_map[app_label]
    
    # 核心应用只在 default 迁移
    core_apps = ['system', 'auth', 'contenttypes', 'sessions']
    if app_label in core_apps:
        return db == 'default'
    
    # 其他应用默认在 default
    return db == 'default'
```

---

## 常见问题

### Q1: 为什么配置 `'dvadmin_twodev.basedata.park': 'dm'` 不生效？

**A**: 应该使用 `app_label` 而不是完整路径。

```python
# ❌ 错误
app_db_map = {
    'dvadmin_twodev.basedata.park': 'dm',
}

# ✅ 正确
app_db_map = {
    'park': 'dm',
}
```

**原因**：Django 路由器使用 `model._meta.app_label`，它是应用名的最后一部分。

### Q2: 报错 "Cannot assign ... prevents this relation"

**A**: 跨数据库外键关联被阻止。

**解决**：路由器已配置允许 `Users` 的跨数据库关联（审计字段）。

### Q3: 表创建在 SYSDBA 而不是 MHGJ_DC

**A**: Schema 没有正确设置。

**解决**：
1. 检查 `settings.py` 中的 `NAME` 配置
2. 确认 `base.py` 中的 `init_connection_state` 方法
3. 手动迁移表到正确的 Schema：

```sql
-- 方法1：重建
DROP TABLE SYSDBA.DWD_PARK;
-- 然后重新执行 migrate

-- 方法2：重命名
ALTER TABLE SYSDBA.DWD_PARK RENAME TO MHGJ_DC.DWD_PARK;
```

### Q4: 连接报错 "oracle_mode is an invalid keyword"

**A**: OPTIONS 中配置了不支持的参数。

**解决**：清空 OPTIONS 或只保留支持的参数：

```python
"OPTIONS": {},  # 推荐
```

### Q5: 报错 "TypeError: 'class Meta' got invalid attribute(s): db_label"

**A**: Django 的 `Meta` 类不支持 `db_label` 属性。

**原因**：Django 的 `Meta` 类只支持预定义的属性，`db_label` 不是标准属性。

**解决**：必须在 `apps.py` 的 `ready()` 方法中动态设置：

```python
# ❌ 错误：在 Meta 类中设置
class MyModel(models.Model):
    class Meta:
        db_table = "my_table"
        db_label = "dm"  # 会报错！

# ✅ 正确：在 apps.py 的 ready() 方法中设置
# apps.py
class MyAppConfig(AppConfig):
    def ready(self):
        from .models import MyModel
        MyModel._meta.db_label = "dm"
```

**为什么必须在 `ready()` 中设置**：
- Django 在模型类定义时，`_meta` 对象还未完全初始化
- `ready()` 方法在应用完全初始化后调用，此时可以安全地设置属性

### Q6: 如何验证路由是否生效？

**A**: 创建测试脚本：

```python
from dvadmin_twodev.basedata.park.models import ParkModel
from dvadmin.utils.db_router import DatabaseRouter

router = DatabaseRouter()
print(f"app_label: {ParkModel._meta.app_label}")
print(f"路由到: {router.db_for_read(ParkModel)}")
```

### Q7: 如何查看 SQL 执行在哪个数据库？

**A**: 开启 SQL 日志：

```python
# settings.py
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
        },
    },
}
```

---

## 最佳实践

### 1. 数据库选择原则

| 数据类型 | 推荐数据库 | 原因 |
|---------|-----------|------|
| 系统核心数据 | Default (Vastbase) | 用户、权限、认证 |
| 业务基础数据 | DM (达梦) | 停车场、车辆、线路 |
| 统计分析数据 | DM (达梦) | OD数据、OSM数据 |
| 临时数据 | Default | 会话、缓存 |

### 2. 迁移顺序

```bash
# 1. 先迁移 default 数据库（核心应用）
python manage.py migrate

# 2. 再迁移 dm 数据库（业务应用）
python manage.py migrate park --database=dm
python manage.py migrate vehicle --database=dm
```

### 3. 性能优化

```python
# 使用 using() 显式指定数据库
ParkModel.objects.using('dm').all()

# 批量操作指定数据库
ParkModel.objects.using('dm').bulk_create([...])

# 原生 SQL 查询
from django.db import connections
with connections['dm'].cursor() as cursor:
    cursor.execute("SELECT ...")
```

### 4. 代码组织

```
backend/
├── dvadmin/                    # 核心模块（default 数据库）
│   ├── system/
│   └── utils/
├── dvadmin_twodev/            # 业务模块（可路由到 dm）
│   ├── basedata/
│   │   ├── park/             # 路由到 dm
│   │   ├── vehicle/          # 路由到 dm
│   │   └── roadline/         # 路由到 dm
│   └── od/
│       ├── od_details/       # 路由到 dm
│       └── od_device/        # 路由到 dm
```

### 5. 测试建议

```python
# tests.py
from django.test import TestCase

class ParkModelTest(TestCase):
    databases = ['default', 'dm']  # 声明使用的数据库
    
    def test_create_park(self):
        """测试创建停车场"""
        park = ParkModel.objects.create(
            park_name="测试停车场"
        )
        self.assertEqual(park._state.db, 'dm')  # 验证使用的数据库
```

### 6. 监控和日志

```python
# 自定义中间件记录数据库使用情况
class DatabaseLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # 记录请求使用的数据库
        response = self.get_response(request)
        return response
```

---

## 附录

### A. 达梦数据库特性

- 兼容 Oracle 语法
- 支持 MVCC
- 支持表空间
- 支持分区表
- 支持存储过程

### B. 相关文件

| 文件 | 说明 |
|------|------|
| `backend/dvadmin/database/dm/__init__.py` | 达梦数据库包初始化 |
| `backend/dvadmin/database/dm/base.py` | 数据库连接和操作 |
| `backend/dvadmin/database/dm/compiler.py` | SQL 编译器 |
| `backend/dvadmin/database/dm/features.py` | 数据库特性定义 |
| `backend/dvadmin/database/dm/operations.py` | 数据库操作 |
| `backend/dvadmin/utils/db_router.py` | 数据库路由器 |
| `backend/application/settings.py` | 数据库配置 |

### C. 参考链接

- [Django 多数据库文档](https://docs.djangoproject.com/en/stable/topics/db/multi-db/)
- [达梦数据库官网](https://www.dameng.com/)
- [dmPython 文档](https://eco.dameng.com/document/dm/zh-cn/pm/python-rogramming-guide.html)

---

## 更新日志

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2025-10-27 | 初始版本，完成达梦数据库集成 |
| 1.0.1 | 2025-10-27 | 修复 app_label 路由问题 |
| 1.0.2 | 2025-10-27 | 添加跨数据库软关联支持 |

---

## 联系方式

如有问题，请联系：
- 作者：王晨
- 日期：2025-10-27

