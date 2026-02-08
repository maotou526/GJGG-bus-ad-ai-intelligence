# 达梦数据库快速入门

## 5分钟快速开始

### 1. 配置路由（1分钟）

编辑 `backend/dvadmin/utils/db_router.py`：

```python
app_db_map = {
    'park': 'dm',  # 将 park 模块路由到达梦数据库
}
```

**⚠️ 注意**：使用 `app_label`（如 `'park'`），不是完整路径！

### 2. 执行迁移（2分钟）

```bash
cd backend

# 创建迁移文件
python manage.py makemigrations park

# 在达梦数据库执行迁移
python manage.py migrate park --database=dm
```

### 3. 验证（2分钟）

```bash
# 测试路由
python -c "
import os, sys, django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'application.settings')
django.setup()
from dvadmin_twodev.basedata.park.models import ParkModel
from dvadmin.utils.db_router import DatabaseRouter
router = DatabaseRouter()
print(f'✅ ParkModel 路由到: {router.db_for_read(ParkModel)}')
print(f'📊 记录数: {ParkModel.objects.count()}')
"
```

### 4. 使用（持续）

现在 `ParkModel` 的所有操作都会自动路由到达梦数据库：

```python
# 创建
park = ParkModel.objects.create(park_name="测试停车场")

# 查询
parks = ParkModel.objects.all()

# 更新
park.park_name = "新名称"
park.save()

# 删除
park.delete()
```

---

## 常用命令

```bash
# 查看迁移状态
python manage.py showmigrations park --database=dm

# 回滚迁移
python manage.py migrate park zero --database=dm

# 查看 SQL
python manage.py sqlmigrate park 0001
```

---

## 故障排查

### 路由不生效？

检查 app_label：

```python
from your_app.models import YourModel
print(YourModel._meta.app_label)  # 使用这个值配置路由
```

### 跨数据库关联报错？

确认路由器允许 Users 关联：

```python
# db_router.py 中应该有
if obj1.__class__ == Users or obj2.__class__ == Users:
    return True
```

---

## 完整文档

查看 [README.md](README.md) 获取详细文档。

