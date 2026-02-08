# 达梦数据库常见问题 (FAQ)

## 目录

1. [配置问题](#配置问题)
2. [路由问题](#路由问题)
3. [迁移问题](#迁移问题)
4. [Schema问题](#schema问题)
5. [性能问题](#性能问题)
6. [错误排查](#错误排查)

---

## 配置问题

### Q1: 为什么配置完整路径 `'dvadmin_twodev.basedata.park': 'dm'` 不生效？

**原因**：Django 路由器使用 `model._meta.app_label`，它是应用名称的**最后一部分**。

**示例**：
```python
# apps.py
class ParkConfig(AppConfig):
    name = "dvadmin_twodev.basedata.park"
    # Django 自动提取 app_label = "park"
```

**正确配置**：
```python
app_db_map = {
    'park': 'dm',  # ✅ 使用 app_label
}
```

**验证方法**：
```python
from dvadmin_twodev.basedata.park.models import ParkModel
print(ParkModel._meta.app_label)  # 输出: 'park'
```

---

### Q2: 如何知道应用的 app_label 是什么？

**方法1：查看模型**
```python
from your_app.models import YourModel
print(YourModel._meta.app_label)
```

**方法2：查看 apps.py**
```python
# apps.py
class YourConfig(AppConfig):
    name = "a.b.c.your_app"
    # app_label 就是 "your_app"（最后一部分）
```

**规律**：
- `dvadmin_twodev.basedata.park` → `park`
- `dvadmin_twodev.od.od_details` → `od_details`
- `dvadmin_twodev.thirdpartydata.poi` → `poi`

---

### Q3: OPTIONS 配置报错 "invalid keyword argument"

**错误示例**：
```python
"OPTIONS": {
    "oracle_mode": False,  # ❌ dmPython 不支持
    "connect_timeout": 10,  # ❌ dmPython 不支持
}
```

**正确配置**：
```python
"OPTIONS": {},  # ✅ 保持为空
```

---

## 路由问题

### Q4: 如何验证路由是否生效？

**测试脚本**：
```python
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()

from your_app.models import YourModel
from dvadmin.utils.db_router import DatabaseRouter

router = DatabaseRouter()
db = router.db_for_read(YourModel)

print(f"app_label: {YourModel._meta.app_label}")
print(f"路由到数据库: {db}")
print(f"配置映射: {router.app_db_map}")

if db == 'dm':
    print("✅ 路由配置正确")
else:
    print("❌ 路由配置错误")
```

---

### Q5: 报错 "Cannot assign ... prevents this relation"

**完整错误**：
```
Cannot assign "<Users: superadmin>": the current database router prevents this relation.
```

**原因**：ParkModel（在 dm）关联 Users（在 default），路由器阻止跨数据库关联。

**解决**：路由器已配置允许 Users 的跨数据库软关联：

```python
def allow_relation(self, obj1, obj2, **hints):
    from dvadmin.system.models import Users
    
    # 允许 Users 的跨数据库关联（审计字段）
    if obj1.__class__ == Users or obj2.__class__ == Users:
        return True
    
    return db1 == db2
```

**验证**：检查 `backend/dvadmin/utils/db_router.py` 的 `allow_relation` 方法。

---

### Q6: 如何让多个应用使用达梦数据库？

**配置**：
```python
app_db_map = {
    'park': 'dm',
    'vehicle': 'dm',
    'roadline': 'dm',
    'od_details': 'dm',
    'od_device': 'dm',
}
```

**迁移**：
```bash
python manage.py migrate park --database=dm
python manage.py migrate vehicle --database=dm
python manage.py migrate roadline --database=dm
```

---

## 迁移问题

### Q7: 迁移时提示 "No migrations to apply"

**原因1**：忘记加 `--database=dm`

```bash
# ❌ 错误（操作 default 数据库）
python manage.py migrate park

# ✅ 正确（操作 dm 数据库）
python manage.py migrate park --database=dm
```

**原因2**：迁移已经执行过了

```bash
# 查看迁移状态
python manage.py showmigrations park --database=dm
```

---

### Q8: 如何回滚迁移？

**回滚到初始状态**：
```bash
python manage.py migrate park zero --database=dm
```

**回滚到指定迁移**：
```bash
python manage.py migrate park 0002 --database=dm
```

**删除迁移记录**：
```sql
-- 在达梦数据库中执行
DELETE FROM DJANGO_MIGRATIONS WHERE app = 'park';
```

---

### Q9: 迁移时核心应用（auth、contenttypes）也迁移到 dm 了怎么办？

**原因**：路由器的 `allow_migrate` 配置有问题。

**检查配置**：
```python
def allow_migrate(self, db, app_label, model_name=None, **hints):
    # 核心应用只在 default 迁移
    core_apps = ['system', 'auth', 'contenttypes', 'sessions', 'admin']
    if app_label in core_apps:
        return db == 'default'
    
    # park 应用只在 dm 迁移
    if app_label in self.app_db_map:
        return db == self.app_db_map[app_label]
    
    return db == 'default'
```

**清理错误迁移**：
```bash
# 在 dm 数据库回滚
python manage.py migrate auth zero --database=dm
python manage.py migrate contenttypes zero --database=dm
```

---

## Schema问题

### Q10: 表创建在 SYSDBA 而不是 MHGJ_DC

**原因**：Schema 没有正确切换。

**检查1**：`settings.py` 配置
```python
"dm": {
    "NAME": "mhgj_dc",  # ✅ 正确设置 Schema 名称
}
```

**检查2**：`base.py` 的 `init_connection_state`
```python
def init_connection_state(self):
    schema_name = self.settings_dict.get('NAME', '').upper()
    if schema_name:
        cursor.execute(f"ALTER SESSION SET CURRENT_SCHEMA = {schema_name}")
```

**解决方法1**：删除并重建
```bash
# 回滚迁移
python manage.py migrate park zero --database=dm

# 在达梦数据库中删除表
# DROP TABLE SYSDBA.DWD_PARK;

# 重新迁移
python manage.py migrate park --database=dm
```

**解决方法2**：移动表
```sql
-- 在达梦数据库中执行
ALTER TABLE SYSDBA.DWD_PARK RENAME TO MHGJ_DC.DWD_PARK;
```

---

### Q11: 如何查询表在哪个 Schema？

**方法1：SQL 查询**
```sql
SELECT owner, table_name 
FROM ALL_TABLES 
WHERE table_name = 'DWD_PARK';
```

**方法2：Python 脚本**
```python
from django.db import connections

with connections['dm'].cursor() as cursor:
    cursor.execute("""
        SELECT owner, table_name 
        FROM ALL_TABLES 
        WHERE table_name = 'DWD_PARK'
    """)
    print(cursor.fetchall())
```

---

### Q12: 如何查看当前连接的 Schema？

```sql
SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL;
```

或 Python：
```python
from django.db import connections

with connections['dm'].cursor() as cursor:
    cursor.execute("SELECT SYS_CONTEXT('USERENV', 'CURRENT_SCHEMA') FROM DUAL")
    current_schema = cursor.fetchone()[0]
    print(f"当前 Schema: {current_schema}")
```

---

## 性能问题

### Q13: 查询很慢怎么办？

**检查1：索引**
```sql
-- 查看表的索引
SELECT index_name, column_name 
FROM USER_IND_COLUMNS 
WHERE table_name = 'DWD_PARK';

-- 创建索引
CREATE INDEX idx_park_name ON DWD_PARK(park_name);
```

**检查2：执行计划**
```sql
EXPLAIN PLAN FOR
SELECT * FROM DWD_PARK WHERE park_name = '测试';

SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

**检查3：Django ORM 优化**
```python
# ❌ N+1 查询
parks = ParkModel.objects.all()
for park in parks:
    print(park.creator.name)  # 每次查询数据库

# ✅ select_related 优化
parks = ParkModel.objects.select_related('creator').all()
for park in parks:
    print(park.creator.name)  # 一次查询
```

---

### Q14: 如何开启 SQL 日志？

**临时开启**：
```python
import logging
logging.getLogger('django.db.backends').setLevel(logging.DEBUG)
```

**永久开启**（`settings.py`）：
```python
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

---

## 错误排查

### Q15: 连接报错 "'int' object has no attribute 'strip'"

**完整错误**：
```
AttributeError: 'int' object has no attribute 'strip'
```

**原因**：`base.py` 中 PORT 未转换为字符串。

**检查**：`backend/dvadmin/database/dm/base.py` 第158-161行
```python
# ✅ 应该有 str() 转换
port = settings_dict['OPTIONS'].get('port', str(settings_dict['PORT']).strip())
```

---

### Q16: 连接报错 "FullResultSet"

**原因**：`compiler.py` 未捕获 `FullResultSet` 异常。

**检查**：`backend/dvadmin/database/dm/compiler.py`
```python
from django.core.exceptions import FullResultSet  # ✅ 应该导入

def compile(self, node, select_format=False):
    try:
        # ... 编译逻辑 ...
    except FullResultSet:  # ✅ 应该捕获
        return '', []
```

---

### Q17: 连接报错 "name 'Col' is not defined"

**原因**：`compiler.py` 未导入 `Col`。

**检查**：`backend/dvadmin/database/dm/compiler.py`
```python
from django.db.models.expressions import OrderBy, Exists, Col  # ✅ 应该包含 Col
```

---

### Q18: 如何查看详细的错误堆栈？

**方法1：Django shell**
```bash
python manage.py shell

>>> from dvadmin_twodev.basedata.park.models import ParkModel
>>> ParkModel.objects.all()
# 会显示完整错误
```

**方法2：Python 脚本**
```python
import traceback

try:
    # 你的代码
    ParkModel.objects.create(...)
except Exception as e:
    print("错误信息:", str(e))
    print("\n完整堆栈:")
    traceback.print_exc()
```

---

## 调试技巧

### 使用 Django shell

```bash
python manage.py shell

>>> from dvadmin_twodev.basedata.park.models import ParkModel
>>> from dvadmin.utils.db_router import DatabaseRouter
>>> 
>>> # 测试路由
>>> router = DatabaseRouter()
>>> router.db_for_read(ParkModel)
'dm'
>>> 
>>> # 测试查询
>>> ParkModel.objects.count()
0
>>> 
>>> # 测试连接
>>> from django.db import connections
>>> connections['dm'].ensure_connection()
>>> print("✅ 连接成功")
```

### 查看生成的 SQL

```python
>>> queryset = ParkModel.objects.filter(park_name='测试')
>>> print(queryset.query)
```

### 使用 using() 显式指定数据库

```python
# 强制使用 dm 数据库
ParkModel.objects.using('dm').all()

# 强制使用 default 数据库
ParkModel.objects.using('default').all()
```

---

## 相关文档

- [README.md](README.md) - 完整文档
- [QUICKSTART.md](QUICKSTART.md) - 快速入门

---

## 仍然有问题？

如果以上 FAQ 无法解决你的问题：

1. 检查 Django 日志和错误堆栈
2. 查看达梦数据库日志
3. 阅读完整文档 [README.md](README.md)
4. 联系开发团队

---

**更新日期**: 2025-10-27  
**版本**: 1.0.0

