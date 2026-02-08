# 高德地图API工具包

## 📖 简介

本工具包提供对高德地图Web服务API的底层调用封装，专注于API调用本身，不包含业务逻辑处理。

**设计原则：**
- ✅ 只负责API调用和数据返回
- ✅ 返回高德API的原始数据
- ❌ 不做数据转换、验证等业务逻辑
- ❌ 不处理坐标系转换（业务层自行处理）

**官方文档：** https://lbs.amap.com/api/webservice/summary

---

## 📁 目录结构

```
gaode/
├── __init__.py              # 包初始化，导出工具类
├── base_client.py           # 基础客户端，处理HTTP请求
├── district_utils.py        # 行政区划API工具 ✅
├── regeo_utils.py           # 逆地理编码API工具 ✅
├── poi_utils.py             # POI搜索API工具（待实现）
├── usage_example.py         # 行政区划使用示例
├── regeo_example.py         # 逆地理编码使用示例
└── README.md                # 使用文档
```

---

## 🚀 快速开始

### 1. 行政区划API

#### 基础用法

```python
from dvadmin_twodev.utils.gaode import DistrictUtils

# 初始化客户端（自动使用配置文件中的API密钥）
client = DistrictUtils()

# 获取苏州市基础信息
data = client.get_district('苏州市')
print(data['districts'][0]['name'])  # 输出：苏州市
```

#### 获取多级行政区

```python
# 获取苏州市及下一级区县
data = client.get_district('苏州市', subdistrict=1)

# 获取苏州市及下两级（区县+街道）
data = client.get_district('苏州市', subdistrict=2)

# 获取苏州市及下三级
data = client.get_district('苏州市', subdistrict=3)
```

#### 获取边界坐标（围栏）

```python
# 方式1：使用 extensions='all'
data = client.get_district('太仓市', subdistrict=1, extensions='all')
fence = data['districts'][0]['polyline']  # 围栏坐标串

# 方式2：使用快捷方法
data = client.get_district_with_boundary('太仓市', subdistrict=2)
fence = data['districts'][0]['polyline']
```

#### 根据行政区划代码查询

```python
# 使用 adcode 查询
data = client.get_district_by_adcode('320585', subdistrict=1)  # 太仓市
```

---

## 📊 返回数据结构

### 基础信息 (extensions='base')

```json
{
    "status": "1",
    "info": "OK",
    "infocode": "10000",
    "count": "1",
    "districts": [
        {
            "citycode": "0512",
            "adcode": "320585",
            "name": "太仓市",
            "center": "121.129772,31.458512",
            "level": "city",
            "districts": [
                {
                    "citycode": "0512",
                    "adcode": "320585",
                    "name": "城厢镇街道",
                    "center": "121.125656,31.455351",
                    "level": "street",
                    "districts": []
                }
            ]
        }
    ]
}
```

### 完整信息 (extensions='all')

在基础信息基础上增加：
```json
{
    "polyline": "121.1,31.4;121.2,31.5;121.3,31.6"  // 边界围栏坐标
}
```

---

## 🔧 在视图中使用

### 示例：在 Django 视图中调用

```python
from rest_framework.decorators import action
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse
from dvadmin_twodev.utils.gaode import DistrictUtils

class DistrictModelViewSet(CustomModelViewSet):
    
    @action(methods=['POST'], detail=False)
    def generate_from_amap(self, request):
        """从高德地图生成行政区数据"""
        
        # 1. 初始化高德API客户端
        gaode_client = DistrictUtils()
        
        try:
            # 2. 调用API获取原始数据
            data = gaode_client.get_district_with_boundary(
                keywords='苏州市',
                subdistrict=2
            )
            
            # 3. 处理业务逻辑（坐标转换、数据入库等）
            districts_data = data.get('districts', [])
            
            # 遍历处理每个行政区
            for district in districts_data:
                adcode = district.get('adcode')
                name = district.get('name')
                center = district.get('center')  # GCJ-02坐标
                polyline = district.get('polyline')  # GCJ-02坐标
                
                # 业务处理：坐标转换
                from dvadmin_twodev.utils.geo import CoordConverter
                if center:
                    lon, lat = center.split(',')
                    wgs_lon, wgs_lat = CoordConverter.gcj02_to_wgs84(
                        (float(lon), float(lat))
                    )
                    center = f"{wgs_lon},{wgs_lat}"
                
                # 业务处理：保存到数据库
                # ...
            
            return SuccessResponse(msg="生成成功")
            
        except Exception as e:
            return ErrorResponse(msg=f"生成失败: {str(e)}")
```

---

## ⚙️ 配置

### API密钥配置

在 `conf/env.py` 中配置高德地图API密钥：

```python
# 高德地图API密钥
AMAP_API_KEY = "your_api_key_here"
```

### 自定义超时时间

```python
# 默认超时30秒
client = DistrictUtils()

# 自定义超时时间（60秒）
client = DistrictUtils(timeout=60)
```

### 使用自定义API密钥

```python
# 使用自定义密钥（不使用配置文件）
client = DistrictUtils(api_key="your_custom_api_key")
```

---

## 🔍 错误处理

### 常见错误

```python
from dvadmin_twodev.utils.gaode import DistrictUtils
import requests

client = DistrictUtils()

try:
    data = client.get_district('苏州市')
except ValueError as e:
    # 参数验证失败
    print(f"参数错误: {e}")
except requests.Timeout:
    # 请求超时
    print("请求超时，请稍后重试")
except requests.RequestException as e:
    # 网络请求失败
    print(f"网络错误: {e}")
except Exception as e:
    # 其他错误（包括高德API返回错误）
    print(f"API调用失败: {e}")
```

### 错误状态码参考

高德API常见错误码：
- `10001`: 密钥不正确
- `10002`: 没有权限使用相应的服务
- `10003`: 访问已超出日访问量
- `10004`: 单位时间内访问过于频繁
- `10005`: IP白名单出错

---

## 📝 注意事项

### 坐标系说明

⚠️ **重要：高德API返回的坐标系为 GCJ-02（火星坐标系）**

- `center`: 中心点坐标（GCJ-02）
- `polyline`: 边界围栏坐标（GCJ-02）

如果需要转换为 WGS84 坐标系，请在业务层使用坐标转换工具：

```python
from dvadmin_twodev.utils.geo import CoordConverter

# GCJ-02 → WGS84
wgs_lon, wgs_lat = CoordConverter.gcj02_to_wgs84((gcj_lon, gcj_lat))
```

### 行政区级别说明

- `country`: 国家
- `province`: 省份/直辖市
- `city`: 城市（地级市）
- `district`: 区县
- `street`: 街道/乡镇

### API调用频率限制

- 免费版：每天调用量有限制
- 建议缓存查询结果，避免重复调用

---

## 🧪 测试

### 单元测试示例

```python
import unittest
from dvadmin_twodev.utils.gaode import DistrictUtils

class TestDistrictUtils(unittest.TestCase):
    
    def setUp(self):
        self.client = DistrictUtils()
    
    def test_get_district(self):
        """测试获取行政区数据"""
        data = self.client.get_district('苏州市')
        
        self.assertEqual(data['status'], '1')
        self.assertIn('districts', data)
        self.assertGreater(len(data['districts']), 0)
        self.assertEqual(data['districts'][0]['name'], '苏州市')
    
    def test_get_district_with_boundary(self):
        """测试获取带边界的行政区数据"""
        data = self.client.get_district_with_boundary('太仓市')
        
        self.assertEqual(data['status'], '1')
        self.assertIn('polyline', data['districts'][0])
    
    def test_invalid_keywords(self):
        """测试无效参数"""
        with self.assertRaises(ValueError):
            self.client.get_district('')
```

---

## 🚀 快速开始（二）

### 2. 逆地理编码API

将经纬度坐标转换为详细的地址信息，获取道路、街道、POI等信息。

**官方文档：** https://lbs.amap.com/api/webservice/guide/api/georegeo

#### 基础用法

```python
from dvadmin_twodev.utils.gaode import RegeoUtils

# 初始化客户端
regeo = RegeoUtils()

# 获取坐标的地址信息
result = regeo.get_address(
    lon=121.123,
    lat=31.456
)

print(result['regeocode']['formatted_address'])  # 完整地址
print(result['regeocode']['addressComponent']['township'])  # 街道
```

#### 获取道路信息

```python
# 获取附近的道路信息（含主干道筛选）
road_info = regeo.get_road_info(
    lon=121.123,
    lat=31.456,
    radius=1000,
    main_road_only=True  # 只返回主干道
)

print(f"道路名称: {road_info['road_name']}")
print(f"所属街道: {road_info['township']}")
print(f"所属区县: {road_info['district']}")

# 附近的道路列表
for road in road_info['roads']:
    print(f"  {road['name']} - 距离{road['distance']}米")
```

#### 查找最近的地铁站

```python
# 查找2km内最近的地铁站
metro = regeo.find_nearest_metro(
    lon=121.123,
    lat=31.456,
    radius=2000
)

if metro['has_metro']:
    print(f"最近地铁站: {metro['metro_name']}")
    print(f"距离: {metro['distance']}米")
else:
    print("附近无地铁站")
```

#### 获取附近POI

```python
# 获取500米内的公交站
pois = regeo.get_nearby_pois(
    lon=121.123,
    lat=31.456,
    radius=500,
    poi_type="公交站"  # 可选：筛选POI类型
)

print(f"地址: {pois['address']}")
for poi in pois['pois']:
    print(f"  {poi['name']} - {poi['distance']}米")
```

#### 综合分析（推荐）

```python
# 一次性获取位置的所有信息
info = regeo.analyze_location(
    lon=121.123,
    lat=31.456,
    radius=1000
)

print(f"完整地址: {info['formatted_address']}")
print(f"省市区: {info['province']} {info['city']} {info['district']}")
print(f"街道: {info['township']}")
print(f"道路: {info['road_name']} {info['street_number']}")

# 地铁信息
if info['nearest_metro']:
    print(f"最近地铁: {info['nearest_metro']['name']}")
    print(f"距离: {info['nearest_metro']['distance']}米")

# 附近道路
for road in info['roads']:
    print(f"  道路: {road['name']} ({road['distance']}米)")

# 附近POI
for poi in info['nearby_pois']:
    print(f"  POI: {poi['name']} ({poi['distance']}米)")
```

#### 批量处理站点数据

```python
# 实际业务场景：批量分析站点信息
from dvadmin_twodev.basedata.roadline_stop.models import RoadlineStopModel

regeo = RegeoUtils()

# 查询所有站点
stops = RoadlineStopModel.objects.all()

for stop in stops:
    try:
        # 分析站点位置
        info = regeo.analyze_location(
            lon=stop.lon02,
            lat=stop.lat02,
            radius=1000
        )
        
        # 更新站点信息
        stop.address = info['formatted_address']
        stop.district = info['district']
        stop.township = info['township']
        stop.road_name = info['road_name']
        
        # 判断是否有地铁接驳
        if info['nearest_metro']:
            stop.has_metro = True
            stop.metro_distance = info['nearest_metro']['distance']
        
        stop.save()
        
    except Exception as e:
        print(f"站点 {stop.stop_name} 分析失败: {e}")
```

#### 原始API调用（高级）

```python
# 直接调用原始API，完全自定义参数
result = regeo.regeo({
    'location': '121.123,31.456',
    'extensions': 'all',       # 返回详细信息
    'radius': 1000,            # 搜索半径
    'roadlevel': 1,            # 只返回主干道
    'poitype': '地铁站|公交站'  # 筛选POI类型
})

# 返回高德API原始数据
print(result)
```

---

## 📊 逆地理编码返回数据说明

### 基础信息 (`extensions=base`)

| 字段 | 说明 | 示例 |
|------|------|------|
| formatted_address | 完整地址 | 江苏省苏州市太仓市城厢镇人民南路123号 |
| province | 省份 | 江苏省 |
| city | 城市 | 苏州市 |
| district | 区县 | 太仓市 |
| township | 街道/乡镇 | 城厢镇 |
| streetNumber.street | 道路名称 | 人民南路 |
| streetNumber.number | 门牌号 | 123号 |

### 扩展信息 (`extensions=all`)

| 字段 | 说明 |
|------|------|
| roads | 附近道路列表 |
| roadinters | 道路交叉口信息 |
| pois | 附近POI列表 |
| aois | 所属AOI信息 |

### 道路信息 (roads)

```python
{
    'name': '人民南路',
    'distance': '12.5',      # 到道路的距离（米）
    'location': '121.123,31.456',
    'direction': '东'
}
```

### POI信息 (pois)

```python
{
    'name': '太仓汽车站',
    'type': '交通设施服务;长途汽车站',
    'distance': '123.5',     # 距离（米）
    'address': '人民南路168号',
    'location': '121.123,31.456'
}
```

---

## 🎯 实际业务场景示例

### 场景1：站点地址自动补全

```python
def auto_fill_stop_address(stop_id):
    """根据站点经纬度自动填充地址信息"""
    from dvadmin_twodev.basedata.roadline_stop.models import RoadlineStopModel
    from dvadmin_twodev.utils.gaode import RegeoUtils
    
    stop = RoadlineStopModel.objects.get(id=stop_id)
    regeo = RegeoUtils()
    
    # 获取地址信息
    info = regeo.analyze_location(stop.lon02, stop.lat02)
    
    # 更新站点信息
    stop.address = info['formatted_address']
    stop.district = info['district']
    stop.township = info['township']
    stop.road_name = info['road_name']
    stop.save()
    
    return info
```

### 场景2：判断站点是否为主干道

```python
def is_main_road_stop(lon, lat):
    """判断站点是否位于主干道"""
    from dvadmin_twodev.utils.gaode import RegeoUtils
    
    regeo = RegeoUtils()
    
    # 只查询主干道
    road_info = regeo.get_road_info(
        lon=lon,
        lat=lat,
        radius=100,  # 100米内
        main_road_only=True
    )
    
    # 如果能找到主干道，说明是主干道站点
    return len(road_info['roads']) > 0
```

### 场景3：站点地铁接驳分析

```python
def analyze_metro_accessibility():
    """分析所有站点的地铁接驳情况"""
    from dvadmin_twodev.basedata.roadline_stop.models import RoadlineStopModel
    from dvadmin_twodev.utils.gaode import RegeoUtils
    
    regeo = RegeoUtils()
    stops = RoadlineStopModel.objects.all()
    
    metro_stops = []
    
    for stop in stops:
        metro = regeo.find_nearest_metro(
            lon=stop.lon02,
            lat=stop.lat02,
            radius=1000  # 1km内算地铁接驳
        )
        
        if metro['has_metro']:
            metro_stops.append({
                'stop_name': stop.stop_name,
                'metro_name': metro['metro_name'],
                'distance': metro['distance']
            })
    
    print(f"共 {len(metro_stops)} 个站点可接驳地铁")
    return metro_stops
```

---

## 📞 支持

如有问题，请参考：
- 高德地图行政区划API文档：https://lbs.amap.com/api/webservice/guide/api/district
- 高德地图逆地理编码API文档：https://lbs.amap.com/api/webservice/guide/api/georegeo
- 项目地理工具文档：`dvadmin_twodev/utils/geo/README.md`

