"""
Description: 站点视图
Version: 1.0
Autor: 王晨
Date: 2025-10-14
LastEditors: 王晨
LastEditTime: 2025-12-12
"""
from rest_framework.decorators import action
from django.db import transaction
from django.db.models import Q
from decimal import Decimal
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import SuccessResponse, DetailResponse, ErrorResponse
from .models import RoadlineStopModel
from .serializers import (
    RoadlineStopModelSerializer,
    RoadlineStopModelListSerializer,
    RoadlineStopSimpleSerializer,
    RoadlineStopImportSerializer,
    RoadlineStopMapSerializer
)
from dvadmin.utils.request_util import get_and_validate_date_param
from django.utils import timezone
from dvadmin_twodev.basedata.roadline_detail.models import RoadlineDetailModel
from dvadmin_twodev.utils.geo.geo_utils import CoordConverter
from rest_framework.permissions import IsAuthenticated
import time


class RoadlineStopModelViewSet(CustomModelViewSet):
    """
    站点管理视图集
    提供标准CRUD接口和数据导入功能
    """
    queryset = RoadlineStopModel.objects.all()
    serializer_class = RoadlineStopModelSerializer

    # 导入序列化器
    import_serializer_class = RoadlineStopImportSerializer

    # 导入字段配置（按照表单字段顺序）
    import_field_dict = {
        'stop_code': '站点编号',
        'district': '区属',
        'roadline_name': '路名',
        'stop_name': '站名',
        'stop_address': '站址',
        'pinyin': '拼音名称',
        'area': '环域',
        'street': '街道',
        'road_line_list': '停靠线路',
        'lon02': '经度',
        'lat02': '纬度',
        'lon84': '经度(WGS84)',
        'lat84': '纬度(WGS84)',
        'stop_type': '站点类型',
        'enabled_mark': '启用状态',
        'remark': '备注',
    }

    @action(methods=['POST'], detail=False, url_path='batch_enrich')
    def batch_enrich(self, request):
        """
        批量填充站点信息
        
        功能说明：
        1. 根据站点名称调用高德公交站点查询API，获取站点编号
        2. 根据经纬度调用高德逆地理编码API，获取地址信息
        3. 使用pypinyin生成拼音名称
        
        请求方式：POST /api/roadline_stop/batch_enrich/
        
        请求参数：
        {
            "stop_ids": [1, 2, 3],  // 可选，指定站点ID列表，不传则处理全部
            "city": "320585"        // 可选，城市adcode，默认320585（太仓）
        }
        
        返回结果：
        {
            "code": 2000,
            "data": {
                "total": 100,
                "success": 95,
                "failed": 5,
                "failed_list": [...]
            },
            "msg": "填充完成！成功 95 条，失败 5 条"
        }
        """
        from dvadmin_twodev.utils.gaode import GaodeAPI

        try:
            # 获取参数
            stop_ids = request.data.get('stop_ids', [])
            city = request.data.get('city', '320585')  # 默认太仓

            # 查询待处理的站点
            if stop_ids:
                stops = self.queryset.filter(id__in=stop_ids)
            else:
                stops = self.queryset.filter(
                    lon02__isnull=False,
                    lat02__isnull=False
                )

            total_count = stops.count()

            if total_count == 0:
                return ErrorResponse(msg="没有需要处理的站点")

            # 初始化工具类
            gaode = GaodeAPI()

            success_count = 0
            failed_list = []

            with transaction.atomic():
                for idx, stop in enumerate(stops):
                    try:
                        # ===== 1. 生成拼音 =====
                        if not stop.pinyin and stop.stop_name:
                            stop.pinyin = self._generate_pinyin(stop.stop_name)

                        # ===== 2. 查询站点编号（高德公交站点API）=====
                        if not stop.stop_code and stop.stop_name:
                            try:
                                bus_result = gaode.bus_stop({
                                    'keywords': stop.stop_name,
                                    'city': city,
                                    'offset': 1  # 只取第一个结果
                                })

                                busstops = bus_result.get('busstops', [])
                                if busstops:
                                    # 取第一个匹配的站点
                                    bus_stop = busstops[0]
                                    stop.stop_code = bus_stop.get('id', '')

                                    # 如果经纬度为空，可以从公交站点数据中获取
                                    if not stop.lon02 or not stop.lat02:
                                        location = bus_stop.get('location', '')
                                        if location:
                                            try:
                                                lon, lat = location.split(',')
                                                stop.lon02 = float(lon)
                                                stop.lat02 = float(lat)
                                            except:
                                                pass

                            except Exception as e:
                                pass

                        # ===== 3. 查询地址信息（逆地理编码API）=====
                        if stop.lon02 and stop.lat02:
                            try:
                                regeo_result = gaode.regeo({
                                    'location': f'{stop.lon02},{stop.lat02}',
                                    'extensions': 'all',
                                    'radius': 500
                                })

                                regeocode = regeo_result.get('regeocode', {})
                                address_component = regeocode.get('addressComponent', {})
                                street_number = address_component.get('streetNumber', {})

                                # 填充地址信息
                                if not stop.district:
                                    stop.district = address_component.get('district', '')

                                if not stop.roadline_name:
                                    stop.roadline_name = street_number.get('street', '')

                                if not stop.street:
                                    stop.street = address_component.get('township', '')

                                if not stop.stop_address:
                                    stop.stop_address = regeocode.get('formatted_address', '')

                                if not stop.path_direction:
                                    stop.path_direction = street_number.get('direction', '')

                                # 区域判断（业务逻辑）
                                if not stop.area:
                                    stop.area = self._determine_area(stop.district, stop.street)

                            except Exception as e:
                                pass

                        # 保存站点
                        stop.save()
                        success_count += 1

                    except Exception as e:
                        failed_list.append({
                            'stop_id': stop.id,
                            'stop_name': stop.stop_name,
                            'reason': str(e)
                        })

            # 返回结果
            return SuccessResponse(
                data={
                    'total': total_count,
                    'success': success_count,
                    'failed': len(failed_list),
                    'failed_list': failed_list[:20]  # 只返回前20个失败项
                },
                msg=f"填充完成！成功 {success_count} 条，失败 {len(failed_list)} 条"
            )

        except Exception as e:
            return ErrorResponse(msg=f"批量填充失败: {str(e)}")

    def _generate_pinyin(self, chinese_name):
        """生成拼音名称"""
        try:
            from pypinyin import lazy_pinyin
            return ''.join(lazy_pinyin(chinese_name))
        except ImportError:
            return ''
        except Exception as e:
            return ''

    def _determine_area(self, district, street):
        """根据行政区和街道判断区域"""
        try:
            # 业务规则：根据实际情况调整
            if '太仓' in district:
                if '城厢' in street:
                    return '中心城区'
                elif '高新' in street or '科教新城' in street:
                    return '高新区'
                elif '港区' in street or '浏河' in street:
                    return '港区'
                elif '沙溪' in street:
                    return '沙溪镇'
                elif '浮桥' in street:
                    return '浮桥镇'
                else:
                    return '其他区域'
            return '未知区域'
        except Exception as e:
            return ''

    def get_stop_coordinates(self, start_date=None, end_date=None, line_ids=None):
        """
        获取启用站点的GCJ02坐标。支持按时间范围和线路ID过滤。
        参数：start_date/end_date为时间范围（可选），line_ids为线路ID列表或'all'（可选，默认全部）。
        返回：包含stop_id、stop_name、lon02、lat02的字典列表，仅包含有效坐标的启用站点。
        示例：viewset.get_stop_coordinates(line_ids=[1,2])
        """
        try:
            # 构建基础查询
            query = self.queryset.filter(
                Q(delete_mark=0) | Q(delete_mark__isnull=True),
                enabled_mark=1,
                lon02__isnull=False,
                lat02__isnull=False
            )

            # 时间范围过滤
            if start_date:
                query = query.filter(exec_day__gte=start_date)
            if end_date:
                query = query.filter(exec_day__lte=end_date)

            # 线路过滤
            if line_ids and line_ids != 'all':
                if isinstance(line_ids, (list, tuple)):
                    from dvadmin_twodev.basedata.roadline_stop_rel.models import RoadlineStopRelModel
                    stop_ids = RoadlineStopRelModel.objects.filter(
                        roadline_id__in=line_ids
                    ).values_list('stop_id', flat=True).distinct()
                    query = query.filter(id__in=stop_ids)

            # 返回坐标数据
            return list(query.values('id', 'stop_id', 'stop_name', 'lon02', 'lat02'))

        except Exception as e:
            return []

    @action(methods=['POST'], detail=False, url_path='auto_fill_data')
    def auto_fill_data(self, request):
        """
        自动填充站点数据（高德逆地理编码API）
        
        功能说明：
        1. 遍历所有有经纬度的站点
        2. 调用高德地图逆地理编码API获取地理位置信息
        3. 从API返回的数据中提取：
           - area（区域）= addressComponent.city（如"苏州市"）
           - district（行政区）= addressComponent.district（如"太仓市"）
           - roadline_name（道路名称）= addressComponent.streetNumber.street（如"县府东街"）
           - street（街道）= addressComponent.township（如"娄东街道"）
           - stop_address（站点地址）= regeocode.formatted_address（完整地址）
        4. 批量更新站点表
        
        请求方式：POST /api/RoadlineStopModelViewSet/auto_fill_data/
        
        请求参数：
        {
            "stop_ids": [1, 2, 3],      // 可选，指定站点ID列表，不传则处理全部
            "amap_key": "xxx",          // 可选，高德地图API Key（不传则从配置读取）
            "batch_size": 100,          // 可选，进度日志输出间隔（默认100）
            "delay": 0.2,               // 可选，每次API调用后的延迟秒数（默认0.2秒）
            "force_update": false       // 可选，是否强制更新已有数据（默认false，只更新空字段）
        }
        
        返回结果：
        {
            "code": 2000,
            "data": {
                "total_stops": 500,
                "success_count": 485,
                "failed_count": 15,
                "skipped_count": 10,        // 无经纬度跳过的数量
                "failed_items": [...],
                "api_call_count": 490,
                "retry_count": 20,
                "retry_success_count": 18,
                "retry_failed_count": 2
            },
            "msg": "自动填充完成！成功 485 条，失败 15 条"
        }
        """
        from dvadmin_twodev.utils.gaode import GaodeAPI
        from django.db.models import Q
        import time

        try:
            # ============= 0. 获取配置参数 =============
            stop_ids = request.data.get('stop_ids', [])
            amap_key = request.data.get('amap_key', None)
            batch_size = int(request.data.get('batch_size', 100))
            delay = float(request.data.get('delay', 0.2))
            force_update = request.data.get('force_update', False)

            # 初始化高德API客户端
            try:
                gaode = GaodeAPI(api_key=amap_key)
            except ValueError as e:
                return ErrorResponse(msg=f"高德API初始化失败: {str(e)}")

            with transaction.atomic():
                # ============= 1. 获取待处理的站点 =============
                if stop_ids:
                    stops_query = self.queryset.filter(id__in=stop_ids)
                else:
                    stops_query = self.queryset.filter(
                        Q(delete_mark=0) | Q(delete_mark__isnull=True)
                    ).exclude(enabled_mark=0)

                # 如果不是强制更新，只处理关键字段为空的站点
                if not force_update:
                    stops_query = stops_query.filter(
                        Q(area__isnull=True) | Q(area='') |
                        Q(district__isnull=True) | Q(district='') | 
                        Q(roadline_name__isnull=True) | Q(roadline_name='') |
                        Q(street__isnull=True) | Q(street='') |
                        Q(stop_address__isnull=True) | Q(stop_address='')
                    )

                stops = list(stops_query)
                total_stops = len(stops)

                if total_stops == 0:
                    return ErrorResponse(msg="没有需要处理的站点")

                # ============= 2. 遍历站点调用高德API =============
                success_count = 0
                failed_count = 0
                skipped_count = 0
                failed_items = []
                retry_stops = []  # 需要重试的站点列表（QPS限流）
                api_call_count = 0

                for idx, stop in enumerate(stops):
                    try:
                        # 检查经纬度
                        if not stop.lon02 or not stop.lat02:
                            skipped_count += 1
                            continue

                        # 调用高德逆地理编码API
                        try:
                            result = gaode.regeo({
                                'location': f'{stop.lon02},{stop.lat02}',
                                'extensions': 'base'
                            })
                            api_call_count += 1

                            # 每次API调用后添加延迟
                            time.sleep(delay)

                            # 提取地址信息
                            regeocode = result.get('regeocode', {})
                            address_component = regeocode.get('addressComponent', {})
                            street_number_raw = address_component.get('streetNumber', {})
                            formatted_address = regeocode.get('formatted_address', '')

                            # 处理 streetNumber 可能是空数组的情况
                            if isinstance(street_number_raw, dict):
                                street_number = street_number_raw
                            else:
                                street_number = {}  # 如果是数组或其他类型，使用空字典

                            # 提取各字段
                            city = address_component.get('city', '')  # 区域（如"苏州市"）
                            district = address_component.get('district', '')  # 行政区（如"太仓市"）
                            township = address_component.get('township', '')  # 街道（如"娄东街道"）
                            road_name = street_number.get('street', '')  # 道路名称（如"县府东街"）

                            # 兜底逻辑：如果道路名称为空或是无效值（如"[]"），使用街道作为兜底
                            if not road_name or road_name.strip() in ['[]', '[ ]', '{}', '{ }']:
                                road_name = township

                            # 更新字段（如果是强制更新或字段为空）
                            updated = False

                            # 更新区域（city）
                            if force_update or not stop.area:
                                stop.area = city
                                updated = True

                            # 更新行政区（district）
                            if force_update or not stop.district:
                                stop.district = district
                                updated = True

                            # 更新道路名称（roadline_name）
                            if force_update or not stop.roadline_name:
                                stop.roadline_name = road_name
                                updated = True

                            # 更新街道（street）
                            if force_update or not stop.street:
                                stop.street = township
                                updated = True

                            # 更新站点地址（stop_address）
                            if force_update or not stop.stop_address:
                                stop.stop_address = formatted_address
                                updated = True

                            if updated:
                                stop.save()
                                success_count += 1
                            else:
                                # 字段已有值且非强制更新
                                skipped_count += 1

                        except Exception as e:
                            # 捕获API调用异常
                            error_msg = str(e)

                            # 判断是否是QPS限流错误
                            if 'CUQPS_HAS_EXCEEDED_THE_LIMIT' in error_msg or 'QPS' in error_msg:
                                retry_stops.append({
                                    'stop': stop,
                                    'reason': '第一次尝试QPS限流'
                                })
                            else:
                                # 其他错误直接记录为失败
                                failed_items.append({
                                    'stop_id': stop.id,
                                    'stop_name': stop.stop_name,
                                    'reason': f'高德API调用失败: {error_msg}'
                                })
                                failed_count += 1

                    except Exception as e:
                        failed_items.append({
                            'stop_id': stop.id,
                            'stop_name': stop.stop_name,
                            'reason': str(e)
                        })
                        failed_count += 1

                # ============= 3. 重试QPS限流失败的站点 =============
                retry_success_count = 0
                retry_failed_count = 0

                if retry_stops:
                    # 等待一段时间再开始重试
                    time.sleep(5)

                    for idx, retry_item in enumerate(retry_stops):
                        try:
                            stop = retry_item['stop']

                            # 检查经纬度
                            if not stop.lon02 or not stop.lat02:
                                retry_failed_count += 1
                                failed_count += 1
                                continue

                            # 重试调用高德API
                            try:
                                result = gaode.regeo({
                                    'location': f'{stop.lon02},{stop.lat02}',
                                    'extensions': 'base'
                                })
                                api_call_count += 1

                                # 重试时使用双倍延迟
                                time.sleep(delay * 2)

                                # 提取地址信息
                                regeocode = result.get('regeocode', {})
                                address_component = regeocode.get('addressComponent', {})
                                street_number_raw = address_component.get('streetNumber', {})
                                formatted_address = regeocode.get('formatted_address', '')

                                # 处理 streetNumber 可能是空数组的情况
                                if isinstance(street_number_raw, dict):
                                    street_number = street_number_raw
                                else:
                                    street_number = {}

                                # 提取各字段
                                city = address_component.get('city', '')
                                district = address_component.get('district', '')
                                township = address_component.get('township', '')
                                road_name = street_number.get('street', '')

                                # 兜底逻辑：如果道路名称为空或是无效值（如"[]"），使用街道作为兜底
                                if not road_name or road_name.strip() in ['[]', '[ ]', '{}', '{ }']:
                                    road_name = township

                                # 更新字段
                                updated = False
                                if force_update or not stop.area:
                                    stop.area = city
                                    updated = True
                                if force_update or not stop.district:
                                    stop.district = district
                                    updated = True
                                if force_update or not stop.roadline_name:
                                    stop.roadline_name = road_name
                                    updated = True
                                if force_update or not stop.street:
                                    stop.street = township
                                    updated = True
                                if force_update or not stop.stop_address:
                                    stop.stop_address = formatted_address
                                    updated = True

                                if updated:
                                    stop.save()
                                    retry_success_count += 1
                                    success_count += 1

                            except Exception as e:
                                # 重试仍然失败
                                failed_items.append({
                                    'stop_id': stop.id,
                                    'stop_name': stop.stop_name,
                                    'reason': f'重试失败: {str(e)}'
                                })
                                retry_failed_count += 1
                                failed_count += 1

                        except Exception as e:
                            failed_items.append({
                                'stop_id': stop.id,
                                'stop_name': stop.stop_name,
                                'reason': f'重试异常: {str(e)}'
                            })
                            retry_failed_count += 1
                            failed_count += 1

                # ============= 4. 返回结果 =============
                data = {
                    'total_stops': total_stops,
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'skipped_count': skipped_count,
                    'failed_items': failed_items[:50],  # 只返回前50个失败项
                    'api_call_count': api_call_count,
                    'retry_count': len(retry_stops),
                    'retry_success_count': retry_success_count,
                    'retry_failed_count': retry_failed_count
                }

                # 构建返回消息
                if retry_stops:
                    msg = (f"自动填充完成！成功 {success_count} 个，失败 {failed_count} 个，"
                           f"跳过 {skipped_count} 个，重试 {len(retry_stops)} 个（成功 {retry_success_count}）")
                else:
                    msg = f"自动填充完成！成功 {success_count} 个，失败 {failed_count} 个，跳过 {skipped_count} 个"

                return SuccessResponse(data=data, msg=msg)

        except Exception as e:
            return ErrorResponse(msg=f"自动填充失败: {str(e)}")

    @action(methods=['POST'], detail=False, url_path='convert_coordinates')
    def convert_coordinates(self, request):
        """
        将站点坐标从GCJ-02（高德坐标系）转换为WGS84（国际标准坐标系）
        
        功能说明：
        1. 读取数据库中的 lon02 和 lat02 字段（GCJ-02坐标）
        2. 使用坐标转换工具类将其转换为 WGS84 坐标系
        3. 将转换后的坐标存储到 lon84 和 lat84 字段
        4. 支持指定站点ID列表或全量转换
        5. 支持强制更新已有数据
        
        请求方式：POST /api/RoadlineStopModelViewSet/convert_coordinates/
        
        请求参数：
        {
            "stop_ids": [1, 2, 3],      // 可选，指定站点ID列表，不传则处理全部
            "force_update": false,      // 可选，是否强制更新已有数据（默认false，只更新空字段）
            "batch_size": 100,          // 可选，进度日志输出间隔（默认100）
            "delay": 0.1                // 可选，每次转换后的延迟秒数（默认0.1秒）
        }
        
        返回结果：
        {
            "code": 2000,
            "data": {
                "total_stops": 500,
                "success_count": 485,
                "failed_count": 15,
                "skipped_count": 10,        // 无经纬度跳过的数量
                "failed_items": [...]
            },
            "msg": "坐标转换完成！成功 485 条，失败 15 条"
        }
        """
        try:
            # ============= 0. 获取配置参数 =============
            stop_ids = request.data.get('stop_ids', [])
            force_update = request.data.get('force_update', False)
            batch_size = int(request.data.get('batch_size', 100))
            delay = float(request.data.get('delay', 0.1))

            with transaction.atomic():
                # ============= 1. 获取待处理的站点 =============
                if stop_ids:
                    stops_query = self.queryset.filter(id__in=stop_ids)
                else:
                    stops_query = self.queryset.filter(
                        Q(delete_mark=0) | Q(delete_mark__isnull=True)
                    )

                # 如果不是强制更新，只处理 lon84/lat84 为空的站点
                if not force_update:
                    stops_query = stops_query.filter(
                        Q(lon84__isnull=True) | Q(lat84__isnull=True)
                    )

                stops = list(stops_query)
                total_stops = len(stops)

                if total_stops == 0:
                    return ErrorResponse(msg="没有需要处理的站点")

                # ============= 2. 遍历站点进行坐标转换 =============
                success_count = 0
                failed_count = 0
                skipped_count = 0
                failed_items = []

                for idx, stop in enumerate(stops):
                    try:
                        # 检查经纬度
                        if not stop.lon02 or not stop.lat02:
                            skipped_count += 1
                            continue

                        # 执行坐标转换
                        try:
                            # 将 GCJ-02 坐标转换为 WGS84
                            # 严格检查经纬度是否为空
                            try:
                                lon02_val = float(stop.lon02) if stop.lon02 else None
                                lat02_val = float(stop.lat02) if stop.lat02 else None

                                if lon02_val is None or lat02_val is None:
                                    skipped_count += 1
                                    continue

                                gcj02_coord = (lon02_val, lat02_val)
                            except (ValueError, TypeError) as e:
                                # 经纬度无法转换为浮点数
                                skipped_count += 1
                                continue

                            wgs84_coord = CoordConverter.gcj02_to_wgs84(gcj02_coord)

                            # 更新字段
                            updated = False

                            # 更新经度84（转换为 Decimal 类型）
                            if force_update or not stop.lon84:
                                stop.lon84 = Decimal(str(wgs84_coord[0]))
                                updated = True

                            # 更新纬度84（转换为 Decimal 类型）
                            if force_update or not stop.lat84:
                                stop.lat84 = Decimal(str(wgs84_coord[1]))
                                updated = True

                            if updated:
                                stop.save()
                                success_count += 1
                            else:
                                # 字段已有值且非强制更新
                                skipped_count += 1

                            # 延迟处理
                            if delay > 0:
                                time.sleep(delay)

                        except Exception as e:
                            # 坐标转换失败
                            error_msg = str(e)
                            failed_items.append({
                                'stop_id': stop.id,
                                'stop_name': stop.stop_name,
                                'lon02': stop.lon02,
                                'lat02': stop.lat02,
                                'reason': error_msg
                            })
                            failed_count += 1

                    except Exception as e:
                        failed_items.append({
                            'stop_id': stop.id,
                            'stop_name': stop.stop_name,
                            'reason': str(e)
                        })
                        failed_count += 1

                # ============= 3. 返回结果 =============
                data = {
                    'total_stops': total_stops,
                    'success_count': success_count,
                    'failed_count': failed_count,
                    'skipped_count': skipped_count,
                    'failed_items': failed_items[:50]  # 只返回前50个失败项
                }

                return SuccessResponse(
                    data=data,
                    msg=f"坐标转换完成！成功 {success_count} 个，失败 {failed_count} 个，跳过 {skipped_count} 个"
                )

        except Exception as e:
            return ErrorResponse(msg=f"坐标转换失败: {str(e)}")

    @action(
        methods=["GET"],
        detail=False,
        url_path="street_coverage_stats",
        permission_classes=[IsAuthenticated],
    )
    def street_coverage_stats(self, request):
        """
        各街道站点覆盖统计
        
        功能说明：
        1. 统计各个街道（street字段）的站点数量
        2. 统计各个街道的线路数量
           - 按线路主表去重（110上行+110下行 = 1条线路）
        3. 统计各个街道的线路总里程
           - 基于线路主表（roadline）的 line_length 字段
           - 每条线路只累加一次，不管有几个走向经过该街道
           - 例如：110路长度15km，即使上下行都经过该街道，也只累加1次 = 15km
        4. 支持按行政区（district）过滤
        5. 返回适合环形图展示的数据格式
        
        统计逻辑：
        区域站点 → 关联表(RoadlineStopRel) → 线路走向(RoadlineDetail) → 线路主表(Roadline)
        按主表线路ID去重统计数量和里程
        
        请求方式：GET /api/RoadlineStopModelViewSet/street_coverage_stats/
        
        查询参数：
        - district: 可选，按行政区过滤（如"太仓市"）
        - enabled_only: 可选，是否只统计启用的站点，默认true
        
        返回结果：
        {
            "code": 2000,
            "data": {
                "stats": [
                    {
                        "street": "娄东街道",
                        "stop_count": 156,
                        "percentage": 31.2,
                        "line_count": 45,           // 唯一线路数（按主表去重）
                        "total_mileage": 650.5      // 主表线路长度总和（每条只算一次）
                    },
                    ...
                ],
                "summary": {
                    "total_stops": 500,
                    "street_count": 8,
                    "avg_stops_per_street": 62.5,
                    "total_lines": 56,              // 所有唯一线路数（按主表去重）
                    "total_mileage": 1177.5         // 所有唯一线路的长度总和
                }
            },
            "msg": "统计成功！共 8 个街道"
        }
        """
        from django.db.models import Q, Count, Sum
        from dvadmin_twodev.basedata.roadline_stop_rel.models import RoadlineStopRelModel
        from dvadmin_twodev.basedata.roadline.models import RoadlineModel

        try:
            # ============= 1. 获取查询参数 =============
            district = request.query_params.get('district', None)
            enabled_only = request.query_params.get('enabled_only', 'true').lower() == 'true'

            # ============= 2. 构建查询条件 =============
            stops_query = self.queryset.filter(
                Q(delete_mark=0) | Q(delete_mark__isnull=True)
            )

            if enabled_only:
                stops_query = stops_query.exclude(enabled_mark=0)

            if district:
                stops_query = stops_query.filter(district__icontains=district)

            # ============= 3. 按街道分组统计 =============
            # 只过滤NULL值，不过滤空字符串（因为Django可能无法正确识别空字符串）
            street_stats = stops_query.filter(
                street__isnull=False
            ).values('street').annotate(
                stop_count=Count('id')
            ).order_by('-stop_count')

            stats_list = list(street_stats)
            total_stops = sum(item['stop_count'] for item in stats_list)
            street_count = len(stats_list)

            if total_stops == 0:
                return SuccessResponse(
                    data={
                        'stats': [],
                        'summary': {
                            'total_stops': 0,
                            'street_count': 0,
                            'avg_stops_per_street': 0
                        }
                    },
                    msg="未找到站点数据"
                )

            # ============= 4. 计算百分比、线路数量和总里程 =============
            formatted_stats = []
            all_line_ids = set()  # 用于汇总所有唯一线路ID（主表去重）

            for item in stats_list:
                street_name = item['street']
                stop_count = item['stop_count']
                percentage = round((stop_count / total_stops) * 100, 1)

                # 查询该街道的所有站点
                street_stops = stops_query.filter(street=street_name)
                stop_names = list(street_stops.values_list('stop_name', flat=True).distinct())

                # 通过站点名称查询关联的线路详情
                # 先获取所有关联的线路详情ID（去重）
                detail_ids = RoadlineStopRelModel.objects.filter(
                    Q(delete_mark=0) | Q(delete_mark__isnull=True),
                    level_name__in=stop_names,
                    line_dtl_id__isnull=False  # 确保有关联的线路详情
                ).exclude(enabled_mark=0).values_list('line_dtl_id', flat=True).distinct()

                detail_ids_list = list(set([did for did in detail_ids if did is not None]))

                # 检查有多少站点名称能在关联表中找到
                matched_stop_names = RoadlineStopRelModel.objects.filter(
                    Q(delete_mark=0) | Q(delete_mark__isnull=True),
                    level_name__in=stop_names
                ).exclude(enabled_mark=0).values_list('level_name', flat=True).distinct()

                # 计算线路数量和总里程
                if detail_ids_list:
                    # 获取线路详情信息及关联的主表线路ID和长度
                    detail_infos = RoadlineDetailModel.objects.filter(
                        Q(delete_mark=0) | Q(delete_mark__isnull=True),
                        id__in=detail_ids_list
                    ).select_related('roadline').values(
                        'id', 
                        'up_down',
                        'roadline_id',
                        'roadline__line_name',
                        'roadline__line_length'
                    )

                    # 收集唯一的主表线路ID及其长度（用字典避免重复累加）
                    unique_roadlines = {}  # {roadline_id: line_length}

                    for info in detail_infos:
                        roadline_id = info['roadline_id']
                        if roadline_id and roadline_id not in unique_roadlines:
                            roadline_length = float(info['roadline__line_length'] or 0)
                            unique_roadlines[roadline_id] = roadline_length

                    # 线路数量 = 唯一的主表线路数（110上行+下行只算1条）
                    line_count = len(unique_roadlines)

                    # 总里程 = 每条线路的长度累加（只算一次）
                    total_mileage = sum(unique_roadlines.values())

                    # 添加到全局线路ID集合
                    all_line_ids.update(unique_roadlines.keys())
                else:
                    line_count = 0
                    total_mileage = 0.0

                formatted_stats.append({
                    'street': street_name,
                    'stop_count': stop_count,
                    'percentage': percentage,
                    'line_count': line_count,
                    'total_mileage': round(total_mileage, 2)
                })

            # ============= 5. 汇总统计（计算所有唯一线路的总里程）=============
            # 按主表线路ID去重，累加主表的线路长度
            if all_line_ids:
                all_roadlines = RoadlineModel.objects.filter(
                    Q(delete_mark=0) | Q(delete_mark__isnull=True),
                    id__in=all_line_ids
                ).values_list('line_length', flat=True)

                # 累加所有唯一线路的长度
                total_mileage_sum = sum([float(length or 0) for length in all_roadlines])
            else:
                total_mileage_sum = 0.0

            summary = {
                'total_stops': total_stops,
                'street_count': street_count,
                'avg_stops_per_street': round(total_stops / street_count, 1) if street_count > 0 else 0,
                'total_lines': len(all_line_ids),  # 唯一线路数量（按主表去重）
                'total_mileage': round(total_mileage_sum, 2)
            }

            # ============= 6. 返回结果 =============
            data = {
                'stats': formatted_stats,
                'summary': summary
            }

            return SuccessResponse(
                data=data,
                msg=f"统计成功！共 {street_count} 个街道，{summary['total_lines']} 条线路"
            )

        except Exception as e:
            return ErrorResponse(msg=f"统计失败: {str(e)}")

    @action(methods=['GET'], detail=False, url_path='get_stop_options')
    def get_stop_options(self, request):
        """
        获取站点选项列表（用于下拉框）
        
        请求方式：GET /api/RoadlineStopModelViewSet/get_stop_options/
        
        请求参数：
        {
            "has_location": true,  // 可选，是否只返回有经纬度的站点，默认false
            "line_id": 1,          // 可选，线路ID（主表ID），如果提供则返回该线路（上行+下行）的所有站点
            "limit": 100           // 可选，返回数量限制，默认100
        }
        
        返回结果：
        {
            "code": 2000,
            "msg": "获取成功",
            "data": [
                {
                    "id": 1,
                    "stop_name": "太仓客运站",
                    "zone": "太仓市",
                    "level_id": 1
                },
                ...
            ]
        }
        """
        from dvadmin_twodev.basedata.roadline_stop_rel.models import RoadlineStopRelModel
        from dvadmin_twodev.basedata.roadline_detail.models import RoadlineDetailModel

        # 获取参数
        has_location = request.query_params.get('has_location', 'false').lower() == 'true'
        line_id = request.query_params.get('line_id', None)
        limit = int(request.query_params.get('limit', 100))

        # 如果提供了线路ID，则直接从关联表查询该线路的站点信息
        if line_id:
            # 1. 先查找该线路的所有详情（上行、下行）
            line_details = RoadlineDetailModel.objects.filter(
                roadline_id=line_id,
                delete_mark=0
            ).values_list('id', flat=True)

            line_detail_ids = list(line_details)

            if not line_detail_ids:
                # 没有找到线路详情，尝试直接查询关联表
                queryset = RoadlineStopRelModel.objects.filter(
                    roadline_id=line_id,
                    delete_mark=0
                )
            else:
                # 2. 直接从关联表查询站点信息
                queryset = RoadlineStopRelModel.objects.filter(
                    line_dtl_id__in=line_detail_ids,
                    delete_mark=0
                )

            # 3. 如果需要筛选有经纬度的站点
            if has_location:
                queryset = queryset.filter(
                    lon02__isnull=False,
                    lat02__isnull=False
                )

            # 4. 查询站点数据，按 level_name 去重（同名站点只保留一个）
            stops = queryset.values(
                'id',
                'level_name',  # 站点名称
                'zone',        # 区属
                'level_id',    # 站序
                'lon02',
                'lat02'
            ).order_by('level_name', 'level_id').distinct('level_name')[:limit]

            stops_list = list(stops)

        else:
            # 全部线路：从关联表查询所有站点（去重）
            queryset = RoadlineStopRelModel.objects.filter(delete_mark=0)

            if has_location:
                queryset = queryset.filter(
                    lon02__isnull=False,
                    lat02__isnull=False
                )

            stops = queryset.values(
                'id',
                'level_name',
                'zone',
                'level_id',
                'lon02',
                'lat02'
            ).order_by('level_name', 'level_id').distinct('level_name')[:limit]

            stops_list = list(stops)

        # 5. 格式化返回数据
        data = [
            {
                'id': stop['id'],
                'stop_name': stop['level_name'] or '未命名站点',
                'zone': stop['zone'] or '',
                'level_id': stop['level_id'] or 0,
                'has_location': bool(stop.get('lon02') and stop.get('lat02'))
            }
            for stop in stops_list
            if stop['level_name']  # 过滤掉没有名称的站点
        ]

        msg = f"获取成功，共{len(data)}个站点"

        return SuccessResponse(data=data, msg=msg)

    def calculate_stop_count(self, start_date=None, end_date=None, line_ids=None, enabled_only=True, group_by='none'):
        """
        计算公交站点总数
        
        功能说明：
        1. 支持按时间范围过滤（基于启用日期和截止日期）
        2. 支持按线路ID过滤（单个、多个或全部线路）
        3. 所有参数都是可选的，如果不传参数则统计全部站点
        4. 支持多种统计维度：总数、按区域分组、按街道分组等
        
        参数：
        - start_date: 可选，开始日期（字符串 YYYY-MM-DD 或 date对象），基于启用日期过滤
        - end_date: 可选，结束日期（字符串 YYYY-MM-DD 或 date对象），基于启用日期过滤
        - line_ids: 可选，线路ID，支持：
          * 单个ID：1
          * 多个ID：[1, 2, 3] 或 "1,2,3"
          * 全部线路："all" 或 None（默认）
        - enabled_only: 可选，是否只统计启用的站点，默认True
        - group_by: 可选，分组统计方式，支持：
          * 'none': 不分组，只返回总数（默认）
          * 'area': 按区域分组
          * 'district': 按行政区分组
          * 'street': 按街道分组
        
        返回结果：
        {
            "total_count": 156,
            "filter_info": {
                "date_range": "2024-01-01 ~ 2024-12-31",
                "line_ids": [1, 2, 3],
                "enabled_only": True
            },
            "groups": [  # 仅当group_by不为'none'时返回
                {
                    "name": "娄东街道",
                    "count": 45,
                    "percentage": 28.8
                },
                ...
            ]
        }
        """
        from django.db.models import Q, Count
        from datetime import datetime

        try:
            # ============= 1. 处理输入参数 =============

            # ============= 2. 构建基础查询条件 =============
            query = Q(delete_mark=0) | Q(delete_mark__isnull=True)

            # 启用状态过滤
            if enabled_only:
                query &= ~Q(enabled_mark=0)

            # 时间范围过滤（基于启用日期）
            if start_date:
                try:
                    if isinstance(start_date, str):
                        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                    else:
                        start_date_obj = start_date  # 假设已经是date对象
                    query &= Q(exec_day__gte=start_date_obj) | Q(exec_day__isnull=True)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"开始日期格式错误，请使用 YYYY-MM-DD 格式或date对象: {str(e)}")

            if end_date:
                try:
                    if isinstance(end_date, str):
                        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                    else:
                        end_date_obj = end_date  # 假设已经是date对象
                    query &= Q(exec_day__lte=end_date_obj) | Q(exec_day__isnull=True)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"结束日期格式错误，请使用 YYYY-MM-DD 格式或date对象: {str(e)}")

            # ============= 3. 处理线路ID过滤 =============
            line_ids_list = []
            if line_ids and str(line_ids).lower() != 'all':
                try:
                    # 解析线路ID列表
                    if isinstance(line_ids, (list, tuple)):
                        line_ids_list = [int(x) for x in line_ids]
                    elif isinstance(line_ids, (int, str)):
                        if isinstance(line_ids, int):
                            line_ids_list = [line_ids]
                        else:
                            line_ids_list = [int(x.strip()) for x in str(line_ids).split(',') if x.strip()]

                    if line_ids_list:
                        # 通过关联表查询包含指定线路的站点名称
                        from dvadmin_twodev.basedata.roadline_stop_rel.models import RoadlineStopRelModel

                        related_stop_names = RoadlineStopRelModel.objects.filter(
                            Q(delete_mark=0) | Q(delete_mark__isnull=True),
                            roadline_id__in=line_ids_list
                        ).exclude(enabled_mark=0).values_list('level_name', flat=True).distinct()

                        stop_names_list = list(set([name for name in related_stop_names if name]))

                        if stop_names_list:
                            query &= Q(stop_name__in=stop_names_list)
                        else:
                            # 没有找到相关站点，返回空结果
                            return {
                                'total_count': 0,
                                'filter_info': {
                                    'date_range': f"{start_date or ''} ~ {end_date or ''}".strip(' ~'),
                                    'line_ids': line_ids_list,
                                    'enabled_only': enabled_only
                                },
                                'groups': []
                            }

                except ValueError as e:
                    raise ValueError(f"线路ID格式错误: {str(e)}")

            # ============= 4. 执行查询 =============
            stops_queryset = self.queryset.filter(query)
            total_count = stops_queryset.count()

            # ============= 5. 分组统计（如果需要）=============
            groups = []
            if group_by != 'none' and total_count > 0:
                group_field_map = {
                    'area': 'area',
                    'district': 'district', 
                    'street': 'street'
                }

                if group_by not in group_field_map:
                    raise ValueError(f"不支持的分组方式: {group_by}")

                group_field = group_field_map[group_by]

                # 按指定字段分组统计
                group_stats = stops_queryset.filter(
                    **{f"{group_field}__isnull": False}
                ).exclude(
                    **{group_field: ''}
                ).values(group_field).annotate(
                    count=Count('id')
                ).order_by('-count')

                # 格式化分组结果
                for item in group_stats:
                    group_name = item[group_field]
                    count = item['count']
                    percentage = round((count / total_count) * 100, 1) if total_count > 0 else 0

                    groups.append({
                        'name': group_name,
                        'count': count,
                        'percentage': percentage
                    })

            # ============= 6. 构建返回数据 =============
            filter_info = {
                'enabled_only': enabled_only
            }

            # 添加日期范围信息
            if start_date or end_date:
                date_range = f"{start_date or ''} ~ {end_date or ''}".strip(' ~')
                filter_info['date_range'] = date_range

            # 添加线路ID信息
            if line_ids_list:
                filter_info['line_ids'] = line_ids_list
            elif line_ids and str(line_ids).lower() == 'all':
                filter_info['line_ids'] = 'all'

            data = {
                'total_count': total_count,
                'filter_info': filter_info
            }

            # 只有在分组时才返回groups字段
            if group_by != 'none':
                data['groups'] = groups

            return data

        except Exception as e:
            raise

    def calculate_street_stop_count(self, start_date=None, end_date=None):
        """
        根据传入的时间范围，返回当前不同街道的站点数量
        
        参数：
        - start_date: 可选，开始日期（字符串 YYYY-MM-DD 或 date对象）
        - end_date: 可选，结束日期（字符串 YYYY-MM-DD 或 date对象）
        
        返回结果：
        {
            "total_count": 156,
            "filter_info": {
                "date_range": "2024-01-01 ~ 2024-12-31"
            },
            "street_stats": [
                {
                    "street": "娄东街道",
                    "count": 45,
                    "percentage": 28.8
                },
                ...
            ]
        }
        """
        from django.db.models import Q, Count
        from datetime import datetime

        try:

            # 构建基础查询条件
            query = Q(delete_mark=0) | Q(delete_mark__isnull=True)
            query &= ~Q(enabled_mark=0)  # 只统计启用的站点

            # 时间范围过滤（基于启用日期）
            if start_date:
                try:
                    if isinstance(start_date, str):
                        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
                    else:
                        start_date_obj = start_date
                    query &= Q(exec_day__gte=start_date_obj) | Q(exec_day__isnull=True)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"开始日期格式错误，请使用 YYYY-MM-DD 格式: {str(e)}")

            if end_date:
                try:
                    if isinstance(end_date, str):
                        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
                    else:
                        end_date_obj = end_date
                    query &= Q(exec_day__lte=end_date_obj) | Q(exec_day__isnull=True)
                except (ValueError, TypeError) as e:
                    raise ValueError(f"结束日期格式错误，请使用 YYYY-MM-DD 格式: {str(e)}")

            # 执行查询获取总数
            stops_queryset = self.queryset.filter(query)
            total_count = stops_queryset.count()

            # 按街道分组统计
            street_stats = []
            if total_count > 0:
                group_stats = stops_queryset.filter(
                    street__isnull=False
                ).exclude(
                    street=''
                ).values('street').annotate(
                    count=Count('id')
                ).order_by('-count')

                # 格式化分组结果
                for item in group_stats:
                    street_name = item['street']
                    count = item['count']
                    percentage = round((count / total_count) * 100, 1) if total_count > 0 else 0

                    street_stats.append({
                        'street': street_name,
                        'count': count,
                        'percentage': percentage
                    })

            # 构建返回数据
            filter_info = {}
            if start_date or end_date:
                date_range = f"{start_date or ''} ~ {end_date or ''}".strip(' ~')
                filter_info['date_range'] = date_range

            data = {
                'total_count': total_count,
                'filter_info': filter_info,
                'street_stats': street_stats
            }

            return data

        except Exception as e:
            raise

    @action(
        methods=["GET"],
        detail=False,
        url_path="get_all",
        permission_classes=[IsAuthenticated],
    )
    def get_all(self, request):
        """
        获取全量数据（仅有效时间范围内的数据）
        
        功能说明：
        1. 自动过滤有效时间范围内的数据（exec_day <= 当前日期 <= expiry_day）
        2. 支持通过 fields 参数控制返回的字段类型
        3. 返回全量数据，不分页
        4. 支持地图展示模式（fields=map），返回WGS84坐标数据
        
        请求参数：
        - fields: 可选，控制返回字段类型
          * simple: 只返回 id、站点编号、站点名称
          * list: 返回列表序列化器的字段（优化后的字段列表）
          * map: 返回地图展示需要的字段（包含WGS84坐标数据）
          * full: 返回全部字段（默认）
        - date: 可选，指定查询日期（格式：YYYY-MM-DD），默认为当前日期
        
        请求示例：
        GET /api/RoadlineStopModelViewSet/get_all/?fields=simple
        GET /api/RoadlineStopModelViewSet/get_all/?fields=list
        GET /api/RoadlineStopModelViewSet/get_all/?fields=map
        GET /api/RoadlineStopModelViewSet/get_all/?fields=full
        GET /api/RoadlineStopModelViewSet/get_all/?fields=map&date=2025-01-01
        
        返回结果：
        {
            "code": 2000,
            "msg": "获取成功，共 100 条数据",
            "data": [...]
        }
        
        地图模式（fields=map）返回示例：
        {
            "code": 2000,
            "msg": "获取成功，共 100 条数据",
            "data": [
                {
                    "id": 1,
                    "stop_code": "STOP001",
                    "stop_name": "太仓客运站",
                    "area": "苏州市",
                    "district": "太仓市",
                    "street": "娄东街道",
                    "stop_address": "江苏省苏州市太仓市...",
                    "lon84": 121.123456,
                    "lat84": 31.456789
                },
                ...
            ]
        }
        """
        try:
            # 获取字段类型参数
            fields_type = request.query_params.get('fields', 'full').lower()

            # 获取日期参数（用于过滤有效时间范围）
            date_param = request.query_params.get('date', None)

            # 如果未传递日期参数，直接使用当天日期
            if not date_param:
                query_date = timezone.now().date()
            else:
                # 如果传递了日期参数，进行验证
                query_date, error_response = get_and_validate_date_param(
                    date_param, 
                    required=False, 
                    date_format='YYYY-MM-DD'
                )

                # 如果验证失败，返回错误
                if error_response:
                    return error_response

            # 根据参数选择序列化器
            if fields_type == 'simple':
                serializer_class = RoadlineStopSimpleSerializer
            elif fields_type == 'list':
                serializer_class = RoadlineStopModelListSerializer
            elif fields_type == 'map':
                serializer_class = RoadlineStopMapSerializer
            else:  # full 或其他
                serializer_class = RoadlineStopModelSerializer

            # 获取基础查询集（应用过滤条件）
            queryset = self.filter_queryset(self.get_queryset())

            # 过滤有效时间范围内的数据（使用 model 中的方法）
            queryset = queryset.valid_period(query_date)
            
            # 序列化数据
            serializer = serializer_class(queryset, many=True, request=request)

            return DetailResponse(
                data=serializer.data,
                msg=f"获取成功，共 {len(serializer.data)} 条数据"
            )

        except Exception as e:
            return ErrorResponse(msg=f"获取数据失败: {str(e)}")
