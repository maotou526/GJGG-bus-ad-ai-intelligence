# 太仓线网常量定义模块

## 概述

本模块为太仓线网项目提供常量定义功能，包含系统常量和业务常量两大类。常量设计遵循Django项目规范，提供统一的配置管理和常量引用。

## 目录结构

```text
backend/dvadmin_twodev/constants/
├── __init__.py              # 模块初始化文件
├── system_constants.py      # 系统常量定义
├── business_constants.py    # 业务常量定义
├── usage_example.py         # 使用示例
└── README.md               # 说明文档
```

## 主要功能

### 1. system_constants.py - 系统常量

提供系统级别的常量配置：

- **系统信息**: 系统标题、版本、描述等
- **状态码**: HTTP状态码和业务状态码
- **状态选择**: 通用状态、审核状态、删除状态等
- **文件配置**: 文件上传限制、允许的文件类型等
- **分页配置**: 默认分页大小、分页选择等
- **缓存配置**: 缓存过期时间、缓存键前缀等
- **日志配置**: 日志级别、格式等
- **时间配置**: 时间格式、时区等
- **验证配置**: 密码强度、用户名规则等
- **导出配置**: 导出文件限制、文件路径等

### 2. business_constants.py - 业务常量

提供太仓线网业务相关的常量配置：

- **项目信息**: 项目标题、副标题、描述等
- **地理信息**: 太仓市基本信息、坐标范围等
- **网格配置**: 网格大小选择、默认配置等
- **交通类型**: 交通工具类型、交通方式等
- **时间配置**: 时间段定义、高峰时间等
- **人口密度**: 密度等级、阈值等
- **职住分析**: 职住类型、平衡指标等
- **数据源配置**: 数据源类型、更新频率等
- **分析类型**: OD分析类型、热力图类型等
- **可视化配置**: 地图样式、颜色方案等
- **权限配置**: 用户角色、数据权限等

## 使用方法

### 基本使用

```python
# 方式1：导入整个常量模块
from dvadmin_twodev.constants import system_constants, business_constants

# 使用系统常量
print(system_constants.SYSTEM_TITLE)  # 输出: 太仓线网
print(system_constants.STATUS_CHOICES)  # 输出: [(True, '启用'), (False, '禁用')]

# 使用业务常量
print(business_constants.PROJECT_TITLE)  # 输出: 太仓线网
print(business_constants.VEHICLE_TYPES)  # 输出: [('bus', '公交车'), ...]
```

### 直接导入常量

```python
# 方式2：导入具体常量
from dvadmin_twodev.constants.system_constants import SYSTEM_TITLE, STATUS_CHOICES
from dvadmin_twodev.constants.business_constants import PROJECT_TITLE, VEHICLE_TYPES

# 直接使用
print(SYSTEM_TITLE)  # 输出: 太仓线网
print(PROJECT_TITLE)  # 输出: 太仓线网
```

### 在Django模型中使用

```python
from django.db import models
from dvadmin_twodev.constants import system_constants, business_constants

class GridModel(models.Model):
    """网格模型"""
    grid_id = models.CharField(
        max_length=50,
        verbose_name="网格ID",
        help_text="网格唯一标识"
    )
    
    grid_size = models.IntegerField(
        choices=business_constants.GRID_SIZE_OPTIONS,
        default=business_constants.DEFAULT_GRID_SIZE,
        verbose_name="网格大小",
        help_text="网格边长（米）"
    )
    
    status = models.BooleanField(
        choices=system_constants.STATUS_CHOICES,
        default=True,
        verbose_name="状态",
        help_text="网格状态"
    )
```

### 在Django视图中使用

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from dvadmin_twodev.constants import system_constants, business_constants

class GridListView(APIView):
    """网格列表视图"""
    
    def get(self, request):
        """获取网格列表"""
        # 使用分页常量
        page_size = request.GET.get('page_size', system_constants.DEFAULT_PAGE_SIZE)
        max_page_size = system_constants.MAX_PAGE_SIZE
        
        # 使用状态常量
        status = request.GET.get('status')
        if status is not None:
            status = status.lower() == 'true'
        
        # 使用业务常量
        grid_size_options = business_constants.GRID_SIZE_OPTIONS
        
        return Response({
            'code': system_constants.STATUS_SUCCESS,
            'msg': '获取成功',
            'data': grid_list
        })
```

### 在序列化器中使用

```python
from rest_framework import serializers
from dvadmin_twodev.constants import business_constants

class GridSerializer(serializers.ModelSerializer):
    """网格序列化器"""
    
    class Meta:
        model = GridModel
        fields = ['id', 'grid_id', 'grid_size', 'status']
    
    def validate_grid_size(self, value):
        """验证网格大小"""
        valid_sizes = [choice[0] for choice in business_constants.GRID_SIZE_OPTIONS]
        if value not in valid_sizes:
            raise serializers.ValidationError("无效的网格大小")
        return value
```

## 运行示例

```bash
# 进入项目目录
cd backend

# 运行使用示例
python dvadmin_twodev/constants/usage_example.py
```

## 常量分类说明

### 系统常量 (system_constants.py)

- **系统信息**: 系统标题、版本等基本信息
- **状态码**: HTTP状态码和业务状态码
- **状态选择**: 各种状态的选择项
- **文件配置**: 文件上传相关配置
- **分页配置**: 分页相关配置
- **缓存配置**: 缓存相关配置
- **日志配置**: 日志相关配置
- **时间配置**: 时间格式和时区配置
- **验证配置**: 数据验证相关配置
- **导出配置**: 数据导出相关配置

### 业务常量 (business_constants.py)

- **项目信息**: 项目相关的基本信息
- **地理信息**: 太仓市的地理信息
- **网格配置**: 网格分析相关配置
- **交通类型**: 交通相关的类型定义
- **时间配置**: 业务时间相关配置
- **人口密度**: 人口密度相关配置
- **职住分析**: 职住分析相关配置
- **数据源配置**: 数据源相关配置
- **分析类型**: 数据分析类型定义
- **可视化配置**: 数据可视化相关配置
- **权限配置**: 权限相关配置

## 注意事项

1. **常量不可修改**: 所有常量都是只读的，不应该在运行时修改
2. **命名规范**: 常量使用全大写下划线命名法
3. **分类清晰**: 按功能分类组织常量，便于维护
4. **文档完整**: 每个常量都有清晰的注释说明
5. **类型一致**: 同类型的常量使用相同的数据结构

## 扩展开发

如需添加新的常量，请遵循以下规范：

1. 在相应的常量文件中添加新常量
2. 使用清晰的命名和注释
3. 保持与现有常量的一致性
4. 更新使用示例
5. 更新README文档

## 版本历史

- v1.0.0 (2024-12-19) - 初始版本，包含系统常量和业务常量
