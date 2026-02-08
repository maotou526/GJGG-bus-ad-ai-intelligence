# 后端开发规范文档

## 目录

- [项目概述](#项目概述)
- [技术栈](#技术栈)
- [项目结构](#项目结构)
- [环境配置](#环境配置)
- [开发规范](#开发规范)
- [快速开始](#快速开始)
- [核心概念](#核心概念)
- [最佳实践](#最佳实践)

---

## 项目概述

本后端项目基于 Django + Django REST Framework 构建，采用前后端分离架构，为太仓线网管理系统提供 RESTful API 服务。

### 核心特性

- **分层架构**: Model → View → Serializer → Permission
- **模块化设计**: 按业务功能拆分应用和视图
- **插件化支持**: 通过 plugins 目录支持功能扩展
- **软删除机制**: 使用软删除而非物理删除
- **审计追踪**: 自动记录创建和修改信息
- **权限控制**: 基于角色的权限控制系统(RBAC)
- **数据权限**: 支持行级和列级数据权限控制
- **字段权限**: `FieldPermissionMixin` 支持字段级显示/编辑控制，确保敏感字段按角色差异化呈现
- **字符串主键**: 核心模型统一使用 36 位 UUID 字符串作为主键，便于跨系统同步
- **API文档**: 集成 Swagger/OpenAPI 文档
- **异步任务**: 支持 Celery 异步任务处理

---

## 技术栈

### 核心框架

- **Django 4.2**: Web 框架
- **Django REST Framework 3.15**: RESTful API 框架
- **djangorestframework-simplejwt 5.4**: JWT 认证

### 数据库

- **PostgreSQL**: 主要数据库(支持 dmPython)
- **MySQL**: 可选数据库
- **Redis**: 缓存和消息队列

### 其他工具

- **drf-yasg**: API 文档生成
- **django-filter**: 数据过滤
- **celery**: 异步任务
- **channels**: WebSocket 支持
- **oss2/cos-python-sdk**: 对象存储支持

完整依赖列表请查看 [requirements.txt](requirements.txt)

---

## 项目结构

```
backend/
├── application/              # Django 项目配置
│   ├── settings.py          # 主配置文件
│   ├── urls.py              # 主 URL 路由
│   ├── wsgi.py              # WSGI 入口
│   ├── asgi.py              # ASGI 入口
│   ├── dispatch.py          # 系统初始化分发
│   └── sse_views.py         # SSE 视图
│
├── conf/                    # 环境配置
│   ├── env.py               # 环境变量配置(本地)
│   └── env.example.py       # 环境变量模板
│
├── dvadmin/                 # 核心应用
│   ├── system/              # 系统管理应用
│   │   ├── models.py        # 用户、角色、权限等模型
│   │   ├── views/           # 视图层(按功能模块拆分)
│   │   └── fixtures/        # 初始数据
│   └── utils/               # 工具类和公共组件
│       ├── models.py        # 基础模型(CoreModel)
│       ├── viewset.py       # 自定义 ViewSet
│       ├── pagination.py    # 分页组件
│       ├── permission.py    # 权限验证
│       └── json_response.py # 响应格式
│
├── dvadmin_twodev/          # 业务模块(核心业务代码)
│   ├── basedata/            # 基础数据模块
│   ├── baseentity/          # 基础实体定义
│   ├── constants/           # 常量定义
│   ├── dto/                 # 数据传输对象
│   ├── od/                  # OD 分析模块
│   ├── osm/                 # OSM 地图数据
│   ├── thirdpartydata/      # 第三方数据
│   ├── tx/                  # 通勤分析模块
│   └── utils/               # 工具类(gaode、geo 等)
│
├── dvadmin_extensions/      # 扩展功能模块
│   └── data_permission/     # 数据权限扩展
│
├── plugins/                 # 插件目录
├── static/                  # 静态文件
├── templates/               # 模板文件
├── logs/                    # 日志文件
│
├── manage.py                # Django 管理命令
├── main.py                  # uvicorn 启动入口
├── gunicorn_conf.py         # Gunicorn 配置
└── requirements.txt         # 依赖列表
```

### 模块说明

| 模块 | 说明 | 职责 |
|-----|------|-----|
| `dvadmin/system` | 系统管理 | 用户、角色、权限、菜单等核心功能 |
| `dvadmin/utils` | 公共工具 | 基础模型、视图基类、权限、分页等 |
| `dvadmin_twodev/basedata` | 基础数据 | 区属、停车场、道路线路等基础数据 |
| `dvadmin_twodev/tx` | 通勤分析 | 网格 OD、公交线路、驾车线路等 |
| `dvadmin_twodev/utils` | 业务工具 | 高德地图 API、地理计算等 |
| `dvadmin_extensions/` | 扩展功能 | 数据权限等可插拔功能 |

---

## 环境配置

### 1. 环境准备

**Python 版本**: Python 3.11+

**数据库**: PostgreSQL 或 MySQL

**Redis**: 版本 5.0+

### 2. 配置文件

复制环境配置模板:

```bash
cp conf/env.example.py conf/env.py
```

编辑 `conf/env.py` 配置数据库和 Redis:

```python
# 数据库配置
DATABASE_ENGINE = "django.db.backends.postgresql"
DATABASE_NAME = 'your_database'
DATABASE_HOST = 'localhost'
DATABASE_PORT = 5432
DATABASE_USER = "your_user"
DATABASE_PASSWORD = 'your_password'

# Redis配置
REDIS_HOST = 'localhost'
REDIS_PASSWORD = 'your_password'
REDIS_DB = 1
CELERY_BROKER_DB = 3

# 其他配置
DEBUG = True
TABLE_PREFIX = "dvadmin_"
```

## 开发规范

### 代码风格

遵循 **PEP 8** 规范:

- 使用 4 个空格缩进
- 行长度不超过 120 个字符
- 函数和方法之间使用两个空行分隔
- 类和顶级函数定义之间使用两个空行分隔
- 导入语句按标准库、第三方库、本地应用分组

### 命名规范

| 类型 | 规范 | 示例 |
|-----|------|-----|
| 类名 | 大驼峰 | `Users`, `SystemRole` |
| 函数/方法 | 小写下划线 | `get_user_info()`, `create_user()` |
| 变量 | 小写下划线 | `user_id`, `user_name` |
| 常量 | 全大写下划线 | `MAX_LENGTH`, `DEFAULT_STATUS` |
| 模型字段 | 小写下划线 | `create_datetime` |

### 文件头部注释

每个 Python 文件必须包含标准头部注释:

```python
'''
Description: 文件功能描述
Version: 1.0
Author: 开发者姓名
Date: YYYY-MM-DD HH:MM:SS
LastEditors: 最后修改者
LastEditTime: YYYY-MM-DD HH:MM:SS
'''
```

或使用详细格式:

```python
# -*- coding: utf-8 -*-

"""
文件功能描述
包含模块功能说明

@author: 开发者姓名
@Created on: YYYY-MM-DD HH:MM:SS
@Remark: 特别说明
"""
```

### 导入规范

导入语句必须按以下顺序分组:

```python
# 1. 标准库导入
import os
import logging
from datetime import datetime

# 2. 第三方库导入
from django.db import models
from rest_framework import serializers
from rest_framework.decorators import action

# 3. Django 相关导入
from django.db import transaction

# 4. 项目内部导入
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.constants import business_constants

# 5. 当前模块导入
from .models import YourModel
from .serializers import YourModelSerializer
```

---

## 快速开始

### 启动开发服务器

**方式1: 使用 Django 自带的开发服务器**

```bash
python manage.py runserver 0.0.0.0:8000
```


### 启动 Celery Worker

```bash
celery -A application worker -l info -P solo --workdir backend
```

### 访问 API 文档

- **Swagger**: http://localhost:8000/swagger/
- **Redoc**: http://localhost:8000/redoc/

### 编写第一个 API

**1. 创建业务模块目录**

> 示例：创建 `your_app` 业务模块，并放置在 `dvadmin_twodev/` 目录下，保持与现有模块结构一致。

```bash
python manage.py startapp your_app dvadmin_twodev/your_app
```

创建完成后，可按需在新应用中补充 `admin.py`、`urls.py`、`tests.py` 等文件内容。

**2. 创建模型** (`models.py`):

```python
from dvadmin_twodev.baseentity.models import BaseDataModel

class YourModel(BaseDataModel):
    """示例模型"""
    name = models.CharField(max_length=200, verbose_name="名称", help_text="模型名称")
    
    class Meta:
        db_table = 'your_table'
        verbose_name = "示例模型"
        verbose_name_plural = verbose_name
```

**3. 创建序列化器** (`serializers.py`):

```python
from dvadmin.utils.serializers import CustomModelSerializer

class YourModelSerializer(CustomModelSerializer):
    """示例序列化器"""
    
    class Meta:
        model = YourModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
```

**4. 创建视图集** (`views.py`):

```python
from dvadmin.utils.viewset import CustomModelViewSet
from .models import YourModel
from .serializers import YourModelSerializer

class YourModelViewSet(CustomModelViewSet):
    """示例视图集"""
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
```

**5. 注册路由** (`urls.py`):

```python
from rest_framework.routers import SimpleRouter
from .views import YourModelViewSet

router = SimpleRouter()
router.register("api/YourModelViewSet", YourModelViewSet)

urlpatterns = []
urlpatterns += router.urls
```

**6. 在 settings.py 注册应用**:

```python
INSTALLED_APPS = [
    # ... 其他应用
    "your_app",
]
```

**7. 生成并应用迁移**:

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 核心概念

### 1. 基础模型层次

```
CoreModel (dvadmin/utils/models.py)
    ├── 审计字段(id, create_datetime, update_datetime, creator, modifier等)
    ├── 软删除支持
    └── 通用查询方法

BaseDataModel (dvadmin_twodev/baseentity/models.py)
    ├── 继承自 CoreModel
    ├── 业务字段(delete_mark, enabled_mark)
    └── 业务特定的通用功能

YourModel (具体业务模型)
    ├── 继承自 BaseDataModel
    └── 具体业务字段
```

**使用规则**:

- 核心系统模型继承 `CoreModel`
- 业务数据模型继承 `BaseDataModel`
- 所有模型必须包含中文说明文档

### 2. 响应格式统一

项目使用自定义响应类，确保所有 API 返回格式一致:

```python
from dvadmin.utils.json_response import SuccessResponse, DetailResponse, ErrorResponse

# 成功响应(列表数据，带分页)
return SuccessResponse(data=serializer.data, msg="获取成功")

# 详情响应(单条数据，无分页)
return DetailResponse(data=serializer.data, msg="获取成功")

# 错误响应
return ErrorResponse(msg="操作失败", code=400)
```

**标准响应结构**:

```json
{
    "code": 2000,           // 状态码(2000=成功, 400=错误)
    "msg": "操作成功",      // 提示信息
    "data": {},             // 实际数据
    "page": 1,              // 当前页码(仅列表接口)
    "limit": 20,            // 每页数量(仅列表接口)
    "total": 100            // 总记录数(仅列表接口)
}
```

### 3. 视图集继承体系

```
ModelViewSet (Django REST Framework)
    ↓
CustomModelViewSet (dvadmin/utils/viewset.py)
    ├── 统一响应格式
    ├── 序列化器自动切换
    ├── 软删除支持
    ├── 数据权限过滤
    ├── 字段权限扩展（可与 `FieldPermissionMixin` 组合限制字段可见/可编辑）
    ├── 导入导出功能
    └── 批量操作支持

YourModelViewSet (具体业务视图集)
    ├── 继承 CustomModelViewSet
    ├── 定义 queryset
    ├── 定义 serializer_class
    └── 自定义业务方法
```

**常用属性配置**:

```python
class YourModelViewSet(CustomModelViewSet):
    queryset = YourModel.objects.all()
    serializer_class = YourModelSerializer
    # 可选：引入字段权限，按角色控制字段可见/可写
    # class inherit: (CustomModelViewSet, FieldPermissionMixin)
    # 请在字段配置中声明 field_permission_options
    
    # 序列化器分场景配置
    create_serializer_class = YourModelCreateSerializer
    update_serializer_class = YourModelUpdateSerializer
    list_serializer_class = YourModelListSerializer
    
    # 排序配置
    ordering_fields = ['field1', 'field2', 'create_datetime']
    ordering = ['-create_datetime']
    
    # 过滤配置
    filterset_fields = ['field1', 'field2']
    search_fields = ['field1__icontains', 'field2']
```

### 4. 序列化器分类

按使用场景定义不同的序列化器:

| 序列化器 | 用途 | 字段特点 |
|---------|------|---------|
| `YourModelSerializer` | 基础序列化器 | 包含所有字段 |
| `YourModelCreateSerializer` | 创建时 | 添加必填字段验证 |
| `YourModelUpdateSerializer` | 更新时 | 防止修改主键和时间字段 |
| `YourModelListSerializer` | 列表查询 | 只包含核心字段 |
| `YourModelExportSerializer` | 导出数据 | 优化导出的字段 |

> 基础序列化器请继承 `dvadmin.utils.serializers.CustomModelSerializer`。它已内置审计字段的自动维护逻辑，能在 `create/update` 时同步写入 `creator`、`modifier` 以及冗余姓名字段，并在关联用户缺失时优雅降级。

### 5. 权限控制

**三级权限体系**:

1. **认证**: 通过 JWT Token 验证用户身份
2. **URL 权限**: 基于角色的菜单和按钮权限
3. **数据权限**: 基于部门和自定义规则的行级数据权限

**数据权限合并策略**:

- 自定义规则(`dvadmin_extensions/data_permission/filters.py`)与标准权限(`dvadmin/utils/filters.py`)都会收集 `Q` 对象并挂载到请求对象上
- `CustomModelViewSet.filter_queryset` 会将所有收集到的 `Q` 对象使用 OR 逻辑合并后再过滤 queryset，保证用户满足任一数据权限规则即可访问
- 如需排查最终的查询条件，可在调试时临时打印 `queryset.query` 观察生成的 SQL

**使用示例**:

```python
from rest_framework.permissions import IsAuthenticated
from dvadmin.utils.permission import CustomPermission

class YourModelViewSet(CustomModelViewSet):
    permission_classes = [IsAuthenticated, CustomPermission]
    
    @action(detail=True, methods=['post'])
    def custom_action(self, request, pk=None):
        """自定义操作"""
        # 权限验证由装饰器自动处理
        return SuccessResponse(msg="操作成功")
```

### 6. 软删除机制

项目使用软删除而非物理删除:

```python
# 普通查询会自动过滤已删除的记录
active_records = YourModel.objects.all()

# 查询包含已删除的记录
all_records = YourModel.objects.filter(is_deleted=None)

# 只查询已删除的记录
deleted_records = YourModel.objects.filter(is_deleted=True)

# 软删除操作
record.delete()  # 自动软删除

# 硬删除操作(谨慎使用)
record.hard_delete()
```

---

## 最佳实践

### 1. 数据库查询优化

**使用 select_related 和 prefetch_related**:

```python
# 外键关系: 使用 select_related
users = Users.objects.select_related('dept').all()

# 多对多关系: 使用 prefetch_related
users = Users.objects.prefetch_related('role').all()

# 组合使用
users = Users.objects.select_related('dept').prefetch_related('role').all()
```

**避免 N+1 查询**:

```python
# ❌ 错误: N+1 查询
users = Users.objects.all()
for user in users:
    print(user.dept.name)  # 每次循环都查一次数据库

# ✅ 正确: 一次查询
users = Users.objects.select_related('dept').all()
for user in users:
    print(user.dept.name)  # 只查一次数据库
```

**只查询需要的字段**:

```python
# 只查询指定字段
users = Users.objects.only('id', 'username', 'name')

# 排除不需要的字段
users = Users.objects.defer('description', 'avatar')
```

### 2. 事务处理

**对写操作使用事务**:

```python
from django.db import transaction

@transaction.atomic
def create_with_relation(request):
    """原子性创建关联数据"""
    user = Users.objects.create(**user_data)
    UserProfile.objects.create(user=user, **profile_data)
    return user

# 或使用上下文管理器
def transfer_data(from_id, to_id):
    with transaction.atomic():
        from_obj = YourModel.objects.get(id=from_id)
        to_obj = YourModel.objects.get(id=to_id)
        # 执行数据转移
        to_obj.data = from_obj.data
        to_obj.save()
```

### 3. 常量管理

**使用统一的常量模块**:

```python
# 系统常量
from dvadmin_twodev.constants import system_constants
# business_constants.PROJECT_TITLE

# 业务常量
from dvadmin_twodev.constants import business_constants
# business_constants.GRID_SIZE_OPTIONS

# 在模型中使用
class GridModel(BaseDataModel):
    grid_size = models.IntegerField(
        choices=business_constants.GRID_SIZE_OPTIONS,
        default=business_constants.DEFAULT_GRID_SIZE,
        verbose_name="网格大小"
    )
```

### 4. 自定义 Action

**使用 `@action` 装饰器定义自定义接口**:

```python
from rest_framework.decorators import action
from django.db.models import Sum

class YourModelViewSet(CustomModelViewSet):
    @action(detail=False, methods=['get'], url_path='statistics')
    def get_statistics(self, request):
        """
        获取统计数据
        
        请求参数:
            - start_date: 开始日期
            - end_date: 结束日期
            
        返回结果:
        {
            "code": 2000,
            "data": {
                "total": 10000,
                "avg": 500
            },
            "msg": "获取成功"
        }
        """
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = self.get_queryset()
        if start_date:
            queryset = queryset.filter(create_datetime__gte=start_date)
        if end_date:
            queryset = queryset.filter(create_datetime__lte=end_date)
        
        total = queryset.aggregate(total=Sum('amount'))['total'] or 0
        
        return SuccessResponse(
            data={'total': total, 'count': queryset.count()},
            msg="获取成功"
        )
```

### 5. 工具类开发

**优先使用项目提供的工具类**:

```python
# 高德地图 API
from dvadmin_twodev.utils.gaode import GaodeAPI

gaode = GaodeAPI()
data = gaode.district(params)

# 地理计算工具
from dvadmin_twodev.utils.geo import GeoCalculator, CoordConverter, GridCalculator

# 坐标转换
wgs_coord = CoordConverter.gcj02_to_wgs84((lon, lat))

# 距离计算
distance = GeoCalculator.haversine_distance(point1, point2)
```

### 6. 错误处理

**统一的错误处理**:

```python
from dvadmin.utils.json_response import ErrorResponse

try:
    # 业务逻辑
    result = complex_operation()
    return SuccessResponse(data=result, msg="操作成功")
except ValueError as e:
    # 参数错误
    return ErrorResponse(msg=f"参数错误: {str(e)}", code=400)
except Exception as e:
    # 其他错误
    logger.error(f"操作失败: {e}", exc_info=True)
    return ErrorResponse(msg="操作失败", code=500)
```

### 7. 日志记录

**使用 Django 的 logging**:

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    """处理数据"""
    try:
        logger.info(f"开始处理数据: {len(data)} 条")
        # 处理逻辑
        result = do_process(data)
        logger.info("数据处理成功")
        return result
    except Exception as e:
        logger.error(f"数据处理失败: {e}", exc_info=True)
        raise
```

### 8. 数据验证

**在序列化器中进行验证**:

```python
from rest_framework import serializers

class YourModelSerializer(CustomModelSerializer):
    def validate_name(self, value):
        """字段级验证"""
        if not value or not value.strip():
            raise serializers.ValidationError("名称不能为空")
        return value.strip()
    
    def validate(self, attrs):
        """对象级验证"""
        attrs = super().validate(attrs)
        
        # 业务逻辑验证
        if attrs.get('start_time') > attrs.get('end_time'):
            raise serializers.ValidationError({
                "end_time": "结束时间必须晚于开始时间"
            })
        
        return attrs
```

### 9. 测试编写

**编写单元测试**:

```python
from django.test import TestCase
from rest_framework.test import APIClient
from .models import YourModel

class YourModelTestCase(TestCase):
    """模型测试"""
    
    def setUp(self):
        """测试准备"""
        self.client = APIClient()
        self.test_data = {
            "name": "测试数据",
            "status": True
        }
    
    def test_create_model(self):
        """测试创建模型"""
        obj = YourModel.objects.create(**self.test_data)
        self.assertIsNotNone(obj.id)
        self.assertEqual(obj.name, "测试数据")
    
    def test_list_api(self):
        """测试列表接口"""
        response = self.client.get('/api/YourModelViewSet/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['code'], 2000)
```

---

## 相关资源

- **API 文档**: http://localhost:8000/swagger/
- **Django 文档**: https://docs.djangoproject.com/
- **DRF 文档**: https://www.django-rest-framework.org/
- **Cursor Rules**: `.cursor/rules/` 目录下的规范文件

---

## 版本历史

| 版本 | 日期 | 说明 |
|-----|------|-----|
| v1.0.0 | 2025-01 | 初始版本 |

---

## 联系方式

如有问题或建议，请联系项目维护团队。
