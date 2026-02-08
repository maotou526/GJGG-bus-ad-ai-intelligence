# 太仓线网地图几何计算工具类

## 概述

本工具类库为太仓线网项目提供地图几何计算功能，包含坐标转换、距离计算、几何运算等常用功能。工具类设计遵循Django项目规范，提供高精度、高性能的地理计算能力。

## 目录结构

```text
backend/dvadmin_twodev/utils/geo/
├── __init__.py          # 模块初始化文件
├── geo_utils.py         # 核心几何计算工具类
├── geo_examples.py      # 使用示例和演示代码
├── test_geo_utils.py    # 单元测试文件
└── README.md           # 说明文档
```

## 主要功能

### 1. GeoCalculator - 地图几何计算工具类

提供基础的地图几何计算功能：

- **距离计算**
  - `calculate_distance_haversine()` - 使用Haversine公式计算距离（适用于短距离）
  - `calculate_distance_vincenty()` - 使用Vincenty公式计算距离（适用于长距离，精度更高）

- **几何判断**
  - `is_point_in_polygon()` - 判断点是否在多边形内
  - `is_point_in_rectangle()` - 判断点是否在矩形内

- **面积计算**
  - `calculate_polygon_area()` - 计算多边形面积

- **方位计算**
  - `calculate_bearing()` - 计算两点间的方位角
  - `calculate_midpoint()` - 计算两点的中点

- **坐标处理**
  - `parse_coord_string()` - 解析坐标字符串
  - `format_coord_string()` - 格式化坐标为字符串
  - `validate_coord_range()` - 验证坐标范围

### 2. CoordConverter - 坐标系转换工具类

支持不同坐标系之间的转换：

- `tencent_to_wgs84()` - 腾讯坐标系转WGS84坐标系
- `wgs84_to_tencent()` - WGS84坐标系转腾讯坐标系

### 3. GridCalculator - 网格计算工具类

专门用于太仓线网项目的网格相关计算：

- `calculate_grid_center()` - 计算网格中心点
- `calculate_grid_area()` - 计算网格面积
- `is_point_in_grid()` - 判断点是否在网格内

## 使用方法

### 基本使用

```python
from dvadmin_twodev.utils.geo import GeoCalculator, CoordConverter, GridCalculator

# 计算两点间距离
point1 = (121.123456, 31.234567)  # 经度, 纬度
point2 = (121.133456, 31.244567)
distance = GeoCalculator.calculate_distance_haversine(point1, point2)
print(f"距离: {distance:.2f} 米")

# 判断点是否在多边形内
polygon = [(121.1, 31.1), (121.2, 31.1), (121.2, 31.2), (121.1, 31.2)]
test_point = (121.15, 31.15)
is_inside = GeoCalculator.is_point_in_polygon(test_point, polygon)
print(f"点是否在多边形内: {is_inside}")

# 坐标系转换
tencent_coord = (121.123456, 31.234567)
wgs84_coord = CoordConverter.tencent_to_wgs84(tencent_coord)
print(f"WGS84坐标: {wgs84_coord}")

# 网格计算
bottom_left = (121.1, 31.1)
top_right = (121.2, 31.2)
center = GridCalculator.calculate_grid_center(bottom_left, top_right)
area = GridCalculator.calculate_grid_area(bottom_left, top_right)
print(f"网格中心: {center}")
print(f"网格面积: {area:.2f} 平方米")
```

### 在Django模型中使用

```python
from django.db import models
from dvadmin_twodev.utils.geo import GeoCalculator, GridCalculator

class GridModel(models.Model):
    grid_id = models.CharField(max_length=20, verbose_name="网格ID")
    bottom_left_coord = models.CharField(max_length=50, verbose_name="左下角坐标")
    top_right_coord = models.CharField(max_length=50, verbose_name="右上角坐标")
    
    def get_center_coord(self):
        """获取网格中心点坐标"""
        bottom_left = GeoCalculator.parse_coord_string(self.bottom_left_coord)
        top_right = GeoCalculator.parse_coord_string(self.top_right_coord)
        if bottom_left and top_right:
            return GridCalculator.calculate_grid_center(bottom_left, top_right)
        return None
    
    def get_area(self):
        """获取网格面积"""
        bottom_left = GeoCalculator.parse_coord_string(self.bottom_left_coord)
        top_right = GeoCalculator.parse_coord_string(self.top_right_coord)
        if bottom_left and top_right:
            return GridCalculator.calculate_grid_area(bottom_left, top_right)
        return 0
    
    def is_point_in_grid(self, point):
        """判断点是否在网格内"""
        bottom_left = GeoCalculator.parse_coord_string(self.bottom_left_coord)
        top_right = GeoCalculator.parse_coord_string(self.top_right_coord)
        if bottom_left and top_right:
            return GridCalculator.is_point_in_grid(point, bottom_left, top_right)
        return False
```

### 在Django视图中使用

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from dvadmin_twodev.utils.geo import GeoCalculator, GridCalculator

class DistanceCalculationView(APIView):
    """距离计算API视图"""
    
    def post(self, request):
        """计算两点间距离"""
        point1 = request.data.get('point1')
        point2 = request.data.get('point2')
        
        if not point1 or not point2:
            return Response({'error': '缺少坐标参数'}, status=400)
        
        try:
            # 解析坐标
            coord1 = GeoCalculator.parse_coord_string(point1)
            coord2 = GeoCalculator.parse_coord_string(point2)
            
            if not coord1 or not coord2:
                return Response({'error': '坐标格式错误'}, status=400)
            
            # 计算距离
            distance = GeoCalculator.calculate_distance_haversine(coord1, coord2)
            
            return Response({
                'distance': distance,
                'distance_km': distance / 1000,
                'point1': coord1,
                'point2': coord2
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=500)
```

## 运行测试

```bash
# 进入项目目录
cd backend

# 运行单元测试
python -m pytest dvadmin_twodev/utils/geo/test_geo_utils.py -v

# 或者使用Django测试命令
python manage.py test dvadmin_twodev.utils.geo.test_geo_utils
```

## 运行示例

```bash
# 进入项目目录
cd backend

# 运行使用示例
python dvadmin_twodev/utils/geo/geo_examples.py
```

## 注意事项

1. **坐标系说明**
   - 默认使用腾讯坐标系
   - 支持WGS84坐标系转换
   - 坐标格式：`(经度, 纬度)`

2. **精度说明**
   - Haversine公式适用于短距离计算（< 100km）
   - Vincenty公式适用于长距离计算，精度更高
   - 距离计算结果单位为米

3. **性能考虑**
   - 大量计算时建议使用批量处理
   - 复杂多边形计算可能较慢，建议缓存结果

4. **错误处理**
   - 所有方法都包含输入验证
   - 无效输入会返回None或False
   - 建议在使用前检查返回值

## 扩展开发

如需添加新的几何计算功能，请遵循以下规范：

1. 在相应的工具类中添加新方法
2. 添加完整的文档字符串和类型注解
3. 编写对应的单元测试
4. 更新使用示例
5. 更新README文档

## 版本历史

- v1.0.0 (2024-12-19) - 初始版本，包含基础几何计算功能
