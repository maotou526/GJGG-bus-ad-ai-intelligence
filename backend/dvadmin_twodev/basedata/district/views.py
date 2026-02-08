'''
Description: 区属视图
Version: 1.0
Autor: AI Assistant
Date: 2025-10-16
LastEditors: 
LastEditTime: 2025-10-17
'''
from django.db import transaction
from rest_framework.decorators import action
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import SuccessResponse, ErrorResponse
from dvadmin_twodev.utils.gaode import GaodeAPI
from dvadmin_twodev.utils.geo import CoordConverter
from .models import DistrictModel
from .serializers import DistrictModelSerializer


class DistrictModelViewSet(CustomModelViewSet):
    """
    区属管理视图集
    提供标准CRUD接口和从高德地图生成区属数据的功能
    """
    queryset = DistrictModel.objects.all()
    serializer_class = DistrictModelSerializer
    
    # 配置基本的过滤和搜索字段
    filterset_fields = ['type', 'enabled_mark', 'delete_mark']
    search_fields = ['name']
    
    def get_queryset(self):
        """
        自定义查询集，支持通过父级ID或父级名称搜索
        """
        queryset = super().get_queryset()
        
        # 处理父级ID过滤
        parent_id = self.request.query_params.get('parent_id', None)
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        
        # 处理父级名称搜索
        parent_name = self.request.query_params.get('parent_name', None)
        if parent_name:
            # 先查找匹配名称的区属ID
            parent_districts = DistrictModel.objects.filter(
                name__icontains=parent_name,
                delete_mark=0
            ).values_list('id', flat=True)
            
            # 然后过滤出这些ID作为parent_id的区属
            queryset = queryset.filter(parent_id__in=parent_districts)
        
        return queryset

    @action(methods=['POST'], detail=False, url_path='generate_from_amap')
    def generate_from_amap(self, request):
        """
        从高德地图生成行政区数据（苏州市及下级县级市、街道）
        
        请求方式：POST /api/DistrictModelViewSet/generate_from_amap/
        
        固定参数：
        - keywords: "苏州市"（固定获取苏州市数据）
        - subdistrict: 2（获取县级市和街道两级数据）
        
        将获取：
        - 苏州市
        - 昆山市、太仓市、张家港市、常熟市、吴江区等
        - 各县级市/区下的街道
        
        返回结果：
        {
            "code": 2000,
            "data": {
                "deleted_count": 10,
                "created_count": 100,
                "root_keywords": "苏州市",
                "subdistrict": 2
            },
            "msg": "生成成功！删除 10 条，创建 100 条区属数据"
        }
        """
        # 固定参数：苏州市及下两级（县级市、街道）
        # 街道级数据的ID会自动生成唯一标识（父级ID + 序号）
        root_keywords = '苏州市'
        subdistrict = 2
        
        try:
            with transaction.atomic():
                # 1. 清空现有数据（物理删除，绕过queryset过滤器）
                # 先检查数据量
                existing_count = DistrictModel.objects.count()
                print(f"[删除前] 数据库中有 {existing_count} 条区属数据")
                
                # 执行删除
                deleted_count = DistrictModel.objects.all().delete()[0]
                print(f"[删除后] 已删除 {deleted_count} 条数据")
                
                # 再次检查
                remaining_count = DistrictModel.objects.count()
                print(f"[删除后验证] 数据库中剩余 {remaining_count} 条数据")
                
                # 2. 调用高德API工具类
                gaode = GaodeAPI()
                params = {
                    'keywords': root_keywords,
                    'subdistrict': subdistrict,
                    'extensions': 'all',  # 获取边界坐标
                    'showbiz': 'false'
                }
                
                data = gaode.district(params)
                
                # 提取行政区数据（工具类已经验证了API返回状态）
                districts_data = data.get('districts', [])
                if not districts_data:
                    raise Exception("未查询到任何行政区数据")
                
                # 3. 递归处理并批量插入
                created_count = 0
                district_list = []
                
                def process_district(district_info, parent_id=None, depth=0, sibling_index=0):
                    """递归处理行政区数据"""
                    nonlocal created_count
                    
                    # 提取数据
                    adcode = district_info.get('adcode')
                    name = district_info.get('name')
                    center = district_info.get('center', '')
                    level = district_info.get('level', '')
                    polyline = district_info.get('polyline', '')
                    
                    # 转换中心点坐标：高德地图坐标 → WGS84（使用坐标转换工具类）
                    if center:
                        try:
                            lon, lat = center.split(',')
                            wgs_lon, wgs_lat = CoordConverter.gcj02_to_wgs84((float(lon), float(lat)))
                            center = f"{wgs_lon},{wgs_lat}"
                        except (ValueError, IndexError) as e:
                            print(f"[警告] 中心点坐标转换失败: {center}, 错误: {e}")
                    
                    # 转换围栏坐标：高德地图坐标 → WGS84
                    if polyline:
                        try:
                            # 手动循环转换每个坐标点
                            coords = []
                            for pair in polyline.split(';'):
                                lon_str, lat_str = pair.split(',')
                                wgs_lon, wgs_lat = CoordConverter.gcj02_to_wgs84((float(lon_str), float(lat_str)))
                                coords.append(f"{wgs_lon},{wgs_lat}")
                            polyline = ';'.join(coords)
                        except Exception as e:
                            print(f"[警告] 围栏坐标转换失败，将保留原始值，错误: {e}")
                    
                    # 映射level到type
                    level_map = {
                        'country': '国',
                        'province': '省',
                        'city': '市',
                        'district': '区',
                        'street': '街道'
                    }
                    district_type = level_map.get(level, level)
                    
                    # 处理街道级数据的ID冲突问题
                    # 如果是街道且adcode与父级相同，生成唯一ID
                    unique_id = adcode
                    if level == 'street' and parent_id and adcode == parent_id:
                        # 使用父级ID + 3位序号作为唯一ID（如：320505001）
                        unique_id = f"{parent_id}{sibling_index:03d}"
                    
                    # 调试日志
                    indent = "  " * depth
                    children_count = len(district_info.get('districts', []))
                    id_info = f"原ID:{adcode}, 唯一ID:{unique_id}" if unique_id != adcode else adcode
                    print(f"{indent}[处理] {name} ({id_info}) - {district_type} - 子级数量: {children_count}")
                    
                    # 创建区属对象
                    district_obj = DistrictModel(
                        id=unique_id,  # 使用唯一ID
                        name=name,
                        type=district_type,
                        parent_id=parent_id,
                        center_coord=center,
                        fence=polyline,
                        enabled_mark=1,
                        delete_mark=0
                    )
                    district_list.append(district_obj)
                    created_count += 1
                    
                    # 递归处理子级
                    if 'districts' in district_info and district_info['districts']:
                        print(f"{indent}  → 递归处理 {len(district_info['districts'])} 个子级")
                        for idx, child in enumerate(district_info['districts']):
                            process_district(child, parent_id=unique_id, depth=depth+1, sibling_index=idx+1)
                
                # 处理所有行政区数据
                for district in districts_data:
                    process_district(district)
                
                # 4. 批量创建（使用 update_or_create 避免主键冲突）
                for district_obj in district_list:
                    DistrictModel.objects.update_or_create(
                        id=district_obj.id,
                        defaults={
                            'name': district_obj.name,
                            'type': district_obj.type,
                            'parent_id': district_obj.parent_id,
                            'center_coord': district_obj.center_coord,
                            'fence': district_obj.fence,
                            'enabled_mark': district_obj.enabled_mark,
                            'delete_mark': district_obj.delete_mark,
                        }
                    )
                
                return SuccessResponse(
                    data={
                        'deleted_count': deleted_count,
                        'created_count': created_count,
                        'root_keywords': root_keywords,
                        'subdistrict': subdistrict
                    },
                    msg=f"生成成功！删除 {deleted_count} 条，创建 {created_count} 条区属数据"
                )
                
        except Exception as e:
            # 统一异常处理（包括高德API调用异常、坐标转换异常等）
            return ErrorResponse(msg=f"生成失败: {str(e)}")
