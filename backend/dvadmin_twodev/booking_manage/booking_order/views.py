'''
Description: 预订订单视图
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-02-02
'''
from typing import List, Dict
from rest_framework.decorators import action
from rest_framework import status
from django.db import transaction
from django.db.models import Q

from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import BookingOrderModel
from .serializers import (
    BookingOrderModelSerializer,
    BookingOrderModelCreateSerializer,
    BookingOrderModelUpdateSerializer,
    BookingOrderModelListSerializer
)

# 导入相关模型
from dvadmin_twodev.booking_manage.booking_order_detail.models import BookingOrderDetailModel
from dvadmin_twodev.booking_manage.vehicle_ad_position.models import VehicleAdPositionModel
from dvadmin_twodev.basedata.vehicle_ad_resource.models import VehicleAdResourceModel
from dvadmin_twodev.basedata.vehicle.models import VehicleModel
from dvadmin_twodev.basedata.media_type.models import AdMediaTypeModel
from dvadmin_twodev.basedata.media_type_composition.models import AdMediaTypeCompositionModel


class BookingOrderModelViewSet(CustomModelViewSet):
    """
    预订订单管理视图集
    
    功能说明:
    - 提供预订订单的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作
    - 创建/更新订单时自动分配车位
    
    标准DRF接口:
    - GET /api/BookingOrderModelViewSet/ - 获取预订订单列表
    - POST /api/BookingOrderModelViewSet/ - 创建预订订单
    - PUT /api/BookingOrderModelViewSet/{id}/ - 更新预订订单
    - DELETE /api/BookingOrderModelViewSet/{id}/ - 删除预订订单
    
    自定义接口:
    - POST /api/BookingOrderModelViewSet/{id}/allocate_positions/ - 手动触发车位分配
    - POST /api/BookingOrderModelViewSet/{id}/release_positions/ - 释放车位分配
    """
    # 查询集
    queryset = BookingOrderModel.objects.all()
    
    # 默认序列化器(用于查询详情)
    serializer_class = BookingOrderModelSerializer
    
    # 列表序列化器(用于列表展示)
    list_serializer_class = BookingOrderModelListSerializer
    
    # 创建序列化器
    create_serializer_class = BookingOrderModelCreateSerializer
    
    # 更新序列化器
    update_serializer_class = BookingOrderModelUpdateSerializer
    
    # 过滤字段(支持精确查询)
    filter_fields = [
        'id', 'booking_no', 'customer_id', 'customer_name',
        'booking_type', 'booking_status', 'original_booking_id',
        'start_date', 'end_date', 'enabled_mark', 'delete_mark'
    ]
    
    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        'id', 'booking_no', 'customer_id', 'customer_name',
        'booking_type', 'booking_status', 'original_booking_id',
        'start_date', 'end_date', 'enabled_mark', 'delete_mark'
    ]
    
    # 搜索字段(支持模糊查询)
    search_fields = ['booking_no', 'customer_name', 'ad_content']
    
    # 排序字段
    ordering_fields = ['booking_no', 'create_datetime', 'update_datetime', 'start_date', 'end_date', 'booking_status']
    
    # 默认排序
    ordering = ['-create_datetime']
    
    def perform_create(self, serializer):
        """
        创建预订单（不自动分配车位，由前端手动触发）
        
        注意: 前端采用先创建主表，再创建子表的方式
        所以在这里不执行自动分配，而是由前端在子表创建完成后
        手动调用 allocate_positions 接口
        """
        instance = serializer.save()
        # 不在这里自动分配，等待前端手动触发
    
    def perform_update(self, serializer):
        """
        更新预订单后重新分配车位
        """
        instance = serializer.save()
        
        # 先释放旧的车位分配
        try:
            self._release_positions_for_order(instance.id)
        except Exception as e:
            pass
        
        # 重新分配车位
        try:
            result = self._allocate_positions_for_order(instance.id)
            if not result['success']:
                pass
        except Exception as e:
            pass
    
    @action(detail=False, methods=['post'], url_path='create_with_allocation')
    def create_with_allocation(self, request):
        """
        创建预订订单并自动分配车位（事务性操作）
        如果车位分配失败，整个订单创建操作都会回滚
        
        POST /api/BookingOrderModelViewSet/create_with_allocation/
        
        请求体:
        {
            "booking_no": "BK-20260202-0001",
            "customer_id": "uuid",
            "booking_type": 1,
            "booking_status": 3,
            "ad_content": "广告内容",
            "booking_order_details": [
                {
                    "roadline_id": "uuid",
                    "roadline_company_id": "uuid",
                    "media_type_id": "uuid",
                    "quantity": 5,
                    "start_date": "2026-02-10",
                    "end_date": "2026-02-27"
                }
            ]
        }
        """
        booking_order = None
        created_detail_ids = []
        
        try:
            with transaction.atomic():
                # 1. 验证并创建主表数据
                main_serializer = self.get_serializer(data=request.data)
                main_serializer.is_valid(raise_exception=True)
                booking_order = main_serializer.save()
                
                # 2. 获取子表数据
                details_data = request.data.get('booking_order_details', [])
                
                if not details_data:
                    raise ValueError("预订订单明细不能为空")
                
                # 3. 创建子表数据
                from dvadmin_twodev.booking_manage.booking_order_detail.serializers import BookingOrderDetailModelCreateSerializer
                
                created_details = []
                for detail_data in details_data:
                    detail_data['booking_order_id'] = booking_order.id
                    detail_serializer = BookingOrderDetailModelCreateSerializer(data=detail_data)
                    detail_serializer.is_valid(raise_exception=True)
                    detail = detail_serializer.save()
                    created_details.append(detail)
                    created_detail_ids.append(detail.id)
                
                # 4. 分配车位（如果失败会抛出异常，触发事务回滚）
                result = self._allocate_positions_for_order(booking_order.id)
                
                if not result['success']:
                    # 构建详细的错误信息
                    error_details = []
                    for failed in result.get('failed_details', []):
                        error_details.append(failed.get('reason', '未知错误'))
                    
                    error_message = f"车位分配失败，订单创建已回滚。\n\n详细信息：\n" + "\n\n".join(error_details)
                    raise ValueError(error_message)
                
                # 5. 返回成功结果
                return SuccessResponse(
                    data={
                        'id': str(booking_order.id),
                        'booking_no': booking_order.booking_no,
                        'allocation_result': result
                    },
                    msg=f"订单创建成功！{result['message']}"
                )
            
        except Exception as e:
            # 双重保险：手动清理数据（以防事务回滚失败）
            if booking_order and booking_order.id:
                try:
                    from dvadmin_twodev.booking_manage.booking_order_detail.models import BookingOrderDetailModel
                    BookingOrderDetailModel.objects.filter(id__in=created_detail_ids).delete()
                    
                    from dvadmin_twodev.booking_manage.booking_order.models import BookingOrderModel
                    BookingOrderModel.objects.filter(id=booking_order.id).delete()
                except Exception:
                    pass
            
            return ErrorResponse(
                msg=f"订单创建失败：{str(e)}",
                code=400,
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='allocate_positions')
    def allocate_positions(self, request, pk=None):
        """
        手动触发车位分配（不推荐使用，建议使用 create_with_allocation）
        
        POST /api/BookingOrderModelViewSet/{id}/allocate_positions/
        """
        booking_order = self.get_object()
        
        try:
            print(f"[车位分配] 开始为订单 {booking_order.id} 分配车位")
            result = self._allocate_positions_for_order(booking_order.id)
            print(f"[车位分配] 分配结果: {result}")
            
            if result['success']:
                return SuccessResponse(
                    data=result,
                    msg=result['message']
                )
            else:
                return ErrorResponse(
                    data=result,
                    msg=result['message'],
                    code=400
                )
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"[车位分配] 异常详情: {error_detail}")
            return ErrorResponse(
                msg=f"车位分配失败: {str(e)}",
                code=500
            )
    
    @action(detail=True, methods=['post'], url_path='release_positions')
    def release_positions(self, request, pk=None):
        """
        释放车位分配
        
        POST /api/BookingOrderModelViewSet/{id}/release_positions/
        """
        booking_order = self.get_object()
        
        try:
            result = self._release_positions_for_order(booking_order.id)
            
            return SuccessResponse(
                data=result,
                msg=result['message']
            )
        except Exception as e:
            return ErrorResponse(
                msg=f"释放车位失败: {str(e)}",
                code=500
            )
    
    # ==================== 车位分配核心逻辑 ====================
    
    @transaction.atomic
    def _allocate_positions_for_order(self, booking_order_id: int) -> Dict:
        """
        为预订单自动分配车位
        
        Args:
            booking_order_id: 预订单ID
            
        Returns:
            Dict: {
                'success': bool,
                'allocated_count': int,
                'failed_details': List[Dict],
                'message': str
            }
        """
        # 获取该订单的所有明细
        details = BookingOrderDetailModel.objects.filter(
            booking_order_id=booking_order_id,
            delete_mark=0,
            enabled_mark=1
        ).select_related(
            'roadline_id',
            'roadline_company_id',
            'media_type_id'
        )
        
        if not details.exists():
            return {
                'success': False,
                'allocated_count': 0,
                'failed_details': [],
                'message': '未找到预订单明细'
            }
        
        allocated_count = 0
        failed_details = []
        
        # 遍历每个明细进行分配
        for detail in details:
            try:
                result = self._allocate_for_detail(detail)
                if result['success']:
                    allocated_count += result['allocated_count']
                else:
                    failed_details.append({
                        'detail_id': detail.id,
                        'roadline_name': detail.roadline_name,
                        'media_type_name': detail.media_type_name,
                        'quantity': detail.quantity,
                        'reason': result['message']
                    })
            except Exception as e:
                failed_details.append({
                    'detail_id': detail.id,
                    'roadline_name': detail.roadline_name,
                    'media_type_name': detail.media_type_name,
                    'quantity': detail.quantity,
                    'reason': str(e)
                })
        
        success = len(failed_details) == 0
        message = f"成功分配 {allocated_count} 个车位"
        if failed_details:
            message += f"，{len(failed_details)} 个明细分配失败"
        
        return {
            'success': success,
            'allocated_count': allocated_count,
            'failed_details': failed_details,
            'message': message
        }
    
    def _allocate_for_detail(self, detail: BookingOrderDetailModel) -> Dict:
        """
        为单个明细分配车位
        
        Args:
            detail: 预订单明细对象
            
        Returns:
            Dict: {
                'success': bool,
                'allocated_count': int,
                'message': str
            }
        """
        # 【修改】使用明细表的投放日期，而不是主表的日期
        start_date = detail.start_date
        end_date = detail.end_date
        
        # 【调试日志】打印is_composite的原始值和类型
        print(f"[分配-详细] 明细ID={detail.id}")
        print(f"[分配-详细] 使用明细表日期: {start_date} 到 {end_date}")
        print(f"[分配-详细] is_composite原始值={repr(detail.is_composite)}, 类型={type(detail.is_composite)}")
        print(f"[分配-详细] media_type_id={detail.media_type_id}")
        print(f"[分配-详细] media_type_name={detail.media_type_name}")
        
        # 判断是组合类型还是基础类型
        if detail.is_composite:
            print(f"[分配-详细] 判断为组合类型，调用 _allocate_composite_media")
            # 组合类型：需要拆分成基础类型
            return self._allocate_composite_media(detail, start_date, end_date)
        else:
            print(f"[分配-详细] 判断为基础类型，调用 _allocate_base_media")
            # 基础类型：直接分配
            return self._allocate_base_media(detail, start_date, end_date)
    
    def _allocate_composite_media(self, detail: BookingOrderDetailModel, start_date, end_date) -> Dict:
        """
        分配组合类型媒体（如"大三侧" = 车尾+左侧+右侧）
        
        Args:
            detail: 预订单明细对象
            start_date: 投放开始日期
            end_date: 投放结束日期
            
        Returns:
            Dict: 分配结果
        """
        print(f"[组合分配] 开始处理组合类型: {detail.media_type_name}")
        print(f"[组合分配] 媒体类型ID={detail.media_type_id.id}")
        
        # 先查询所有配置（不加过滤条件）
        all_compositions = AdMediaTypeCompositionModel.objects.filter(
            composite_type_id=detail.media_type_id.id  # 【修复】使用.id获取字符串ID
        )
        print(f"[组合分配-调试] 不加过滤条件，找到 {all_compositions.count()} 个配置")
        for comp in all_compositions:
            print(f"[组合分配-调试] 配置: component_type_id={comp.component_type_id}, delete_mark={comp.delete_mark}, enabled_mark={comp.enabled_mark}")
        
        # 获取组合类型包含的基础类型
        compositions = AdMediaTypeCompositionModel.objects.filter(
            composite_type_id=detail.media_type_id.id,  # 【修复】使用.id获取字符串ID
            delete_mark=0,
            enabled_mark=1
        )
        
        print(f"[组合分配] 加过滤条件后，找到 {compositions.count()} 个基础类型配置")
        
        if not compositions.exists():
            error_msg = f"组合类型 {detail.media_type_name} 未配置基础类型"
            print(f"[组合分配] 错误: {error_msg}")
            return {
                'success': False,
                'allocated_count': 0,
                'message': error_msg
            }
        
        # 获取基础类型列表（component_type_id是字符串，需要查询AdMediaTypeModel）
        base_media_type_ids = [comp.component_type_id for comp in compositions]
        print(f"[组合分配] 基础类型ID列表: {base_media_type_ids}")
        
        base_media_types = AdMediaTypeModel.objects.filter(
            id__in=base_media_type_ids,
            delete_mark=0,
            enabled_mark=1
        )
        
        # 打印所有基础类型
        for media_type in base_media_types:
            print(f"[组合分配] 基础类型: {media_type.media_name} (id={media_type.id})")
        print(f"[组合分配] 需要分配的基础类型: {[m.media_name for m in base_media_types]}")
        
        # 查找满足条件的车辆（所有基础类型资源位都可用）
        print(f"[组合分配] 开始查找可用车辆...")
        available_vehicles = self._find_available_vehicles(
            roadline_id=detail.roadline_id.id,
            base_media_types=base_media_types,
            start_date=start_date,
            end_date=end_date,
            quantity=detail.quantity
        )
        
        print(f"[组合分配] 找到 {len(available_vehicles)} 辆可用车辆: {available_vehicles}")
        
        if len(available_vehicles) < detail.quantity:
            # 生成详细的错误提示
            roadline_name = detail.roadline_name or f"线路ID:{detail.roadline_id.id}"
            media_type_name = detail.media_type_name or f"媒体类型ID:{detail.media_type_id.id}"
            base_type_names = "、".join([m.media_name for m in base_media_types])
            date_range = f"{start_date} 至 {end_date}"
            
            error_msg = (
                f"【车辆资源不足】{roadline_name} - {media_type_name}（包含：{base_type_names}）\n"
                f"时间段：{date_range}\n"
                f"需要数量：{detail.quantity} 辆\n"
                f"剩余可用：{len(available_vehicles)} 辆\n"
                f"缺少：{detail.quantity - len(available_vehicles)} 辆"
            )
            
            print(f"[组合分配] 错误: {error_msg}")
            return {
                'success': False,
                'allocated_count': 0,
                'message': error_msg
            }
        
        # 为每辆车的每个基础类型创建车位广告记录
        allocated_count = 0
        for vehicle_id in available_vehicles[:detail.quantity]:
            vehicle = VehicleModel.objects.get(id=vehicle_id)
            print(f"[组合分配] 为车辆 {vehicle.vehicle_no} 分配 {len(base_media_types)} 个基础类型...")
            
            for base_media_type in base_media_types:
                # 获取或创建资源位（包含日期信息）
                resource = self._get_or_create_resource(
                    vehicle_id=vehicle_id,
                    base_media_type_id=base_media_type.id,
                    start_date=start_date,
                    end_date=end_date
                )
                print(f"[组合分配] 资源位: {resource.resource_code}, 基础类型={base_media_type.media_name}")
                
                # 创建车位广告记录
                position = VehicleAdPositionModel.objects.create(
                    booking_detail_id=detail,
                    roadline_id=detail.roadline_id,
                    roadline_name=detail.roadline_name,
                    roadline_company_id=detail.roadline_company_id,
                    roadline_company_name=detail.roadline_company_name,
                    resource_id=resource,
                    vehicle_id_id=vehicle_id,
                    vehicle_no=vehicle.vehicle_no,
                    reserved_start_date=start_date,
                    reserved_end_date=end_date,
                    allocation_status=1,  # 已分配
                    creator=detail.creator,
                    creator_name=detail.creator_name
                )
                print(f"[组合分配] 车位记录创建成功: position_id={position.id}")
                
                allocated_count += 1
                
                # 更新资源位状态为"预订"
                resource.resource_status = 2  # 预订
                # 注意：日期已经在创建时设置，不需要再更新
                # 注意：current_order_id是IntegerField，但订单ID是UUID，暂不设置
                # resource.current_order_id = detail.booking_order_id.id
                resource.save()
                print(f"[组合分配] 资源位状态更新: 预订")
        
        # 更新明细的锁定状态
        detail.lock_status = 2  # 已锁定
        detail.save()
        print(f"[组合分配] 明细锁定状态更新为: 已锁定")
        
        print(f"[组合分配] 分配完成: 成功分配 {detail.quantity} 辆车的 {len(base_media_types)} 个资源位，共 {allocated_count} 条记录")
        return {
            'success': True,
            'allocated_count': allocated_count,
            'message': f"成功分配 {detail.quantity} 辆车的 {len(base_media_types)} 个资源位"
        }
    
    def _allocate_base_media(self, detail: BookingOrderDetailModel, start_date, end_date) -> Dict:
        """
        分配基础类型媒体（如"车头"）
        
        Args:
            detail: 预订单明细对象
            start_date: 投放开始日期
            end_date: 投放结束日期
            
        Returns:
            Dict: 分配结果
        """
        print(f"[基础分配] 开始处理基础类型: {detail.media_type_name}")
        print(f"[基础分配] 线路ID={detail.roadline_id.id}, 线路名={detail.roadline_name}")
        print(f"[基础分配] 媒体类型ID={detail.media_type_id.id}, 媒体类型名={detail.media_type_name}")
        print(f"[基础分配] 需要数量={detail.quantity}, 时间段={start_date} 到 {end_date}")
        
        # 查找满足条件的车辆（单个基础类型资源位可用）
        available_vehicles = self._find_available_vehicles(
            roadline_id=detail.roadline_id.id,
            base_media_types=[detail.media_type_id],
            start_date=start_date,
            end_date=end_date,
            quantity=detail.quantity
        )
        
        print(f"[基础分配] 找到 {len(available_vehicles)} 辆可用车辆: {available_vehicles}")
        
        if len(available_vehicles) < detail.quantity:
            # 生成详细的错误提示
            roadline_name = detail.roadline_name or f"线路ID:{detail.roadline_id.id}"
            media_type_name = detail.media_type_name or f"媒体类型ID:{detail.media_type_id.id}"
            date_range = f"{start_date} 至 {end_date}"
            
            error_msg = (
                f"【车辆资源不足】{roadline_name} - {media_type_name}\n"
                f"时间段：{date_range}\n"
                f"需要数量：{detail.quantity} 辆\n"
                f"剩余可用：{len(available_vehicles)} 辆\n"
                f"缺少：{detail.quantity - len(available_vehicles)} 辆"
            )
            
            print(f"[基础分配] 错误: {error_msg}")
            return {
                'success': False,
                'allocated_count': 0,
                'message': error_msg
            }
        
        # 为每辆车创建车位广告记录
        allocated_count = 0
        for vehicle_id in available_vehicles[:detail.quantity]:
            print(f"[基础分配] 为车辆 {vehicle_id} 创建记录...")
            
            # 获取或创建资源位（包含日期信息）
            resource = self._get_or_create_resource(
                vehicle_id=vehicle_id,
                base_media_type_id=detail.media_type_id.id,
                start_date=start_date,
                end_date=end_date
            )
            print(f"[基础分配] 资源位: {resource.resource_code}, 状态={resource.resource_status}")
            
            # 创建车位广告记录
            vehicle = VehicleModel.objects.get(id=vehicle_id)
            position = VehicleAdPositionModel.objects.create(
                booking_detail_id=detail,
                roadline_id=detail.roadline_id,
                roadline_name=detail.roadline_name,
                roadline_company_id=detail.roadline_company_id,
                roadline_company_name=detail.roadline_company_name,
                resource_id=resource,
                vehicle_id_id=vehicle_id,
                vehicle_no=vehicle.vehicle_no,
                reserved_start_date=start_date,
                reserved_end_date=end_date,
                allocation_status=1,  # 已分配
                creator=detail.creator,
                creator_name=detail.creator_name
            )
            print(f"[基础分配] 车位记录创建成功: position_id={position.id}, vehicle_no={vehicle.vehicle_no}")
            
            allocated_count += 1
            
            # 更新资源位状态为"预订"
            resource.resource_status = 2  # 预订
            # 注意：日期已经在创建时设置，不需要再更新
            # 注意：current_order_id是IntegerField，但订单ID是UUID，暂不设置
            # resource.current_order_id = detail.booking_order_id.id
            resource.save()
            print(f"[基础分配] 资源位状态更新: 预订, 已分配 {allocated_count}/{detail.quantity}")
        
        # 更新明细的锁定状态
        detail.lock_status = 2  # 已锁定
        detail.save()
        print(f"[基础分配] 明细锁定状态更新为: 已锁定")
        
        print(f"[基础分配] 分配完成: 成功分配 {allocated_count} 个车位")
        return {
            'success': True,
            'allocated_count': allocated_count,
            'message': f"成功分配 {detail.quantity} 个车位"
        }
    
    def _find_available_vehicles(
        self,
        roadline_id: int,
        base_media_types: List[AdMediaTypeModel],
        start_date,
        end_date,
        quantity: int
    ) -> List[int]:
        """
        查找满足条件的可用车辆（紧凑型贪心算法 - Best-Fit Allocation）
        
        算法逻辑:
        1. 查找指定线路的所有车辆
        2. 检查每辆车的所有基础类型资源位是否都可用
        3. 检查时间段内是否有冲突
        4. 计算每辆车的"匹配分"（空闲连续天数）
        5. 按匹配分从小到大排序，优先选择"刚好够用"的车辆
        6. 保留长期空闲的车辆给未来的大订单
        
        Args:
            roadline_id: 线路ID
            base_media_types: 基础媒体类型列表
            start_date: 开始日期
            end_date: 结束日期
            quantity: 需要的数量
            
        Returns:
            List[int]: 可用车辆ID列表（已按最佳适应排序）
        """
        print(f"[紧凑贪心] roadline_id={roadline_id}, 需要数量={quantity}")
        print(f"[紧凑贪心] 基础类型: {[m.media_name for m in base_media_types]}")
        print(f"[紧凑贪心] 时间段: {start_date} 到 {end_date}")
        
        # 查找指定线路的所有可用车辆（只检查delete_mark）
        vehicles = VehicleModel.objects.filter(
            roadline_id=roadline_id,
            delete_mark=0,
            enabled_mark=1
        ).values_list('id', flat=True)
        
        print(f"[紧凑贪心] 该线路下共有 {len(vehicles)} 辆可用车辆")
        if len(vehicles) > 0:
            print(f"[紧凑贪心] 车辆ID列表: {list(vehicles)[:5]}...")  # 只打印前5个
        
        # 存储可用车辆及其匹配分
        available_vehicles_with_score = []
        
        for idx, vehicle_id in enumerate(vehicles):
            print(f"[紧凑贪心] 检查车辆 {idx+1}/{len(vehicles)}: vehicle_id={vehicle_id}")
            
            # 检查该车辆的所有基础类型资源位是否都可用
            is_available = True
            
            for base_media_type in base_media_types:
                print(f"[紧凑贪心]   检查基础类型: {base_media_type.media_name}")
                
                # 检查该资源位在时间段内是否有冲突
                conflicts = VehicleAdPositionModel.objects.filter(
                    vehicle_id=vehicle_id,
                    resource_id__base_media_type_id=base_media_type.id,
                    delete_mark=0,
                    enabled_mark=1,
                    allocation_status__in=[1, 2],  # 已分配或已上刊
                ).filter(
                    # 时间段重叠检测
                    Q(reserved_start_date__lte=end_date) &
                    Q(reserved_end_date__gte=start_date)
                )
                
                if conflicts.exists():
                    print(f"[紧凑贪心]   ✗ 有冲突，冲突数量={conflicts.count()}")
                    is_available = False
                    break
                else:
                    print(f"[紧凑贪心]   ✓ 无冲突")
            
            if is_available:
                # 计算该车辆的匹配分（空闲连续天数）
                fit_score = self._calculate_fit_score(
                    vehicle_id=vehicle_id,
                    base_media_types=base_media_types,
                    start_date=start_date,
                    end_date=end_date
                )
                
                print(f"[紧凑贪心] ✓ 车辆 {vehicle_id} 可用，匹配分={fit_score}")
                available_vehicles_with_score.append((vehicle_id, fit_score))
            else:
                print(f"[紧凑贪心] ✗ 车辆 {vehicle_id} 不可用")
        
        # 按匹配分从小到大排序（优先选择空闲时间刚好够用的车辆）
        available_vehicles_with_score.sort(key=lambda x: x[1])
        
        # 提取车辆ID列表
        sorted_vehicle_ids = [vehicle_id for vehicle_id, score in available_vehicles_with_score]
        
        print(f"[紧凑贪心] 最终找到 {len(sorted_vehicle_ids)} 辆可用车辆")
        if len(sorted_vehicle_ids) > 0:
            print(f"[紧凑贪心] 排序后的前5辆车及匹配分: {available_vehicles_with_score[:5]}")
        
        return sorted_vehicle_ids[:quantity] if len(sorted_vehicle_ids) >= quantity else sorted_vehicle_ids
    
    def _calculate_fit_score(
        self,
        vehicle_id: int,
        base_media_types: List[AdMediaTypeModel],
        start_date,
        end_date
    ) -> int:
        """
        计算车辆的匹配分（Best-Fit Score）
        
        算法逻辑:
        1. 查找该车辆在目标时间段前后的所有预订记录
        2. 计算目标时间段所在的连续空闲天数
        3. 空闲天数越少，匹配分越低，优先级越高
        
        匹配分计算规则:
        - 如果目标时间段刚好在两个订单之间（前后都有订单）：
          匹配分 = 空闲天数（最小，最优）
        - 如果目标时间段只有前面或后面有订单：
          匹配分 = 空闲天数 + 1000（次优）
        - 如果目标时间段前后都没有订单（完全空闲）：
          匹配分 = 999999（最大，最差，保留给未来）
        
        Args:
            vehicle_id: 车辆ID
            base_media_types: 基础媒体类型列表
            start_date: 目标开始日期
            end_date: 目标结束日期
            
        Returns:
            int: 匹配分（越小越优先）
        """
        from datetime import timedelta
        
        # 获取该车辆所有相关资源位的所有预订记录（包括目标时间段前后的）
        base_media_type_ids = [m.id for m in base_media_types]
        
        all_positions = VehicleAdPositionModel.objects.filter(
            vehicle_id=vehicle_id,
            resource_id__base_media_type_id__in=base_media_type_ids,
            delete_mark=0,
            enabled_mark=1,
            allocation_status__in=[1, 2],  # 已分配或已上刊
        ).order_by('reserved_start_date')
        
        if not all_positions.exists():
            # 该车辆完全空闲，保留给未来
            print(f"[匹配分] 车辆 {vehicle_id} 完全空闲，匹配分=999999")
            return 999999
        
        # 查找目标时间段前最近的一个订单
        before_positions = all_positions.filter(
            reserved_end_date__lt=start_date
        ).order_by('-reserved_end_date')
        
        # 查找目标时间段后最近的一个订单
        after_positions = all_positions.filter(
            reserved_start_date__gt=end_date
        ).order_by('reserved_start_date')
        
        before_end_date = None
        after_start_date = None
        
        if before_positions.exists():
            before_end_date = before_positions.first().reserved_end_date
            print(f"[匹配分] 车辆 {vehicle_id} 前一个订单结束日期: {before_end_date}")
        
        if after_positions.exists():
            after_start_date = after_positions.first().reserved_start_date
            print(f"[匹配分] 车辆 {vehicle_id} 后一个订单开始日期: {after_start_date}")
        
        # 计算匹配分
        if before_end_date and after_start_date:
            # 目标时间段刚好在两个订单之间（最优）
            gap_days = (after_start_date - before_end_date).days
            fit_score = gap_days
            print(f"[匹配分] 车辆 {vehicle_id} 在两个订单之间，空闲天数={gap_days}，匹配分={fit_score}")
        elif before_end_date:
            # 只有前面有订单
            gap_days = (start_date - before_end_date).days
            fit_score = gap_days + 1000
            print(f"[匹配分] 车辆 {vehicle_id} 只有前面有订单，空闲天数={gap_days}，匹配分={fit_score}")
        elif after_start_date:
            # 只有后面有订单
            gap_days = (after_start_date - end_date).days
            fit_score = gap_days + 1000
            print(f"[匹配分] 车辆 {vehicle_id} 只有后面有订单，空闲天数={gap_days}，匹配分={fit_score}")
        else:
            # 不应该到这里（前面已经检查过all_positions.exists()）
            fit_score = 999999
            print(f"[匹配分] 车辆 {vehicle_id} 异常情况，匹配分={fit_score}")
        
        return fit_score
    
    def _get_or_create_resource(
        self,
        vehicle_id: int,
        base_media_type_id: int,
        start_date,
        end_date
    ) -> VehicleAdResourceModel:
        """
        获取或创建车辆资源位
        
        Args:
            vehicle_id: 车辆ID
            base_media_type_id: 基础媒体类型ID
            start_date: 投放开始日期
            end_date: 投放结束日期
            
        Returns:
            VehicleAdResourceModel: 资源位对象
        """
        # 尝试获取现有资源位（根据车辆、媒体类型和日期范围）
        resource = VehicleAdResourceModel.objects.filter(
            vehicle_id=vehicle_id,
            base_media_type_id=base_media_type_id,
            scheduled_start_date=start_date,
            scheduled_end_date=end_date,
            delete_mark=0,
            enabled_mark=1
        ).first()
        
        if resource:
            print(f"[获取资源] 找到现有资源位: {resource.resource_code}, 日期={start_date}至{end_date}")
            return resource
        
        # 如果不存在，创建新的资源位
        vehicle = VehicleModel.objects.get(id=vehicle_id)
        media_type = AdMediaTypeModel.objects.get(id=base_media_type_id)
        
        # 资源编码包含日期信息，确保唯一性
        resource_code = f"V{vehicle.vehicle_no}-{media_type.media_name}-{start_date}"
        
        resource = VehicleAdResourceModel.objects.create(
            resource_code=resource_code,
            vehicle_id_id=vehicle_id,
            base_media_type_id_id=base_media_type_id,
            scheduled_start_date=start_date,
            scheduled_end_date=end_date,
            resource_status=1,  # 空闲
            enabled_mark=1,
            delete_mark=0
        )
        print(f"[获取资源] 创建新资源位: {resource.resource_code}, 日期={start_date}至{end_date}")
        
        return resource
    
    @transaction.atomic
    def _release_positions_for_order(self, booking_order_id: int) -> Dict:
        """
        释放预订单的所有车位分配
        
        Args:
            booking_order_id: 预订单ID
            
        Returns:
            Dict: {
                'success': bool,
                'released_count': int,
                'message': str
            }
        """
        # 获取该订单的所有车位广告
        positions = VehicleAdPositionModel.objects.filter(
            booking_detail_id__booking_order_id=booking_order_id,
            delete_mark=0,
            enabled_mark=1
        )
        
        released_count = 0
        
        for position in positions:
            # 获取关联的资源位
            resource = position.resource_id
            
            # 删除车位广告记录（软删除）
            position.delete_mark = 1
            position.save()
            print(f"[释放车位] 软删除车位记录: position_id={position.id}")
            
            # 删除资源位记录（软删除）
            # 因为资源位的唯一键包含日期，所以每个时间段是独立的记录
            # 释放时应该删除该资源位记录
            resource.delete_mark = 1
            resource.resource_status = 4  # 下刊
            resource.save()
            print(f"[释放车位] 软删除资源位: resource_code={resource.resource_code}, 日期={resource.scheduled_start_date}至{resource.scheduled_end_date}")
            
            released_count += 1
        
        # 更新所有明细的锁定状态为"已释放"
        BookingOrderDetailModel.objects.filter(
            booking_order_id=booking_order_id,
            delete_mark=0,
            enabled_mark=1
        ).update(lock_status=3)  # 已释放
        
        return {
            'success': True,
            'released_count': released_count,
            'message': f"成功释放 {released_count} 个车位"
        }
    
    @action(detail=True, methods=['post'], url_path='approve')
    @transaction.atomic
    def approve(self, request, pk=None):
        """
        审核通过预订单，并自动创建上刊订单主表和明细表
        
        POST /api/BookingOrderModelViewSet/{id}/approve/
        
        请求体（可选）:
        {
            "review_comment": "审核意见"
        }
        """
        from datetime import datetime
        import random
        from django.utils import timezone
        
        # 导入上刊订单相关模型和序列化器
        from dvadmin_twodev.airing_manage.on_air_order.models import OnAirOrderModel
        from dvadmin_twodev.airing_manage.on_air_order_detail.models import OnAirOrderDetailModel
        from dvadmin_twodev.airing_manage.on_air_order.serializers import OnAirOrderModelCreateSerializer
        from dvadmin_twodev.airing_manage.on_air_order_detail.serializers import OnAirOrderDetailModelCreateSerializer
        
        booking_order = self.get_object()
        
        # 检查订单状态
        if booking_order.booking_status == 4:
            return ErrorResponse(
                msg="该订单已经审核通过，无需重复审核",
                code=400
            )
        
        if booking_order.booking_status == 7:
            return ErrorResponse(
                msg="该订单已被驳回，无法审核通过",
                code=400
            )
        
        # 检查是否已有上刊订单
        existing_on_air_order = OnAirOrderModel.objects.filter(
            booking_order_id=booking_order.id,
            delete_mark=0
        ).first()
        
        if existing_on_air_order:
            return ErrorResponse(
                msg=f"该预订单已存在上刊订单（订单号：{existing_on_air_order.order_no}），无需重复创建",
                code=400
            )
        
        # 获取审核意见
        review_comment = request.data.get('review_comment', '')
        
        try:
            # 1. 更新预订单状态为"已通过"
            booking_order.booking_status = 4  # 已通过
            booking_order.approved_time = timezone.now()
            booking_order.save()
            
            # 2. 生成上刊订单号（格式：ON-YYYYMMDD-XXXX）
            date_str = datetime.now().strftime('%Y%m%d')
            # 确保订单号唯一
            while True:
                random_str = str(random.randint(1000, 9999))
                order_no = f"ON-{date_str}-{random_str}"
                if not OnAirOrderModel.objects.filter(order_no=order_no).exists():
                    break
            
            # 3. 获取预订单的日期范围（从明细中获取最早和最晚日期）
            details = BookingOrderDetailModel.objects.filter(
                booking_order_id=booking_order.id,
                delete_mark=0,
                enabled_mark=1
            )
            
            if not details.exists():
                return ErrorResponse(
                    msg="该预订单没有明细数据，无法创建上刊订单",
                    code=400
                )
            
            # 计算日期范围
            start_dates = [detail.start_date for detail in details if detail.start_date]
            end_dates = [detail.end_date for detail in details if detail.end_date]
            
            if not start_dates or not end_dates:
                return ErrorResponse(
                    msg="该预订单明细缺少日期信息，无法创建上刊订单",
                    code=400
                )
            
            booking_start_date = min(start_dates)
            booking_end_date = max(end_dates)
            
            # 4. 创建上刊订单主表
            on_air_order_data = {
                'order_no': order_no,
                'booking_order_id': booking_order.id,
                'customer_name': booking_order.customer_name or '',
                'booking_start_date': booking_start_date,
                'booking_end_date': booking_end_date,
                'order_status': 4,  # 已通过
                'approved_time': timezone.now(),
                'remark': review_comment or booking_order.remark or '',
                # 不手动传递creator，让序列化器自动从request中获取
            }
            
            # 传递request上下文，让序列化器自动填充creator等审计字段
            on_air_order_serializer = OnAirOrderModelCreateSerializer(
                data=on_air_order_data,
                context={'request': request}
            )
            on_air_order_serializer.is_valid(raise_exception=True)
            on_air_order = on_air_order_serializer.save()
            
            # 5. 获取该预订单的所有车位广告
            positions = VehicleAdPositionModel.objects.filter(
                booking_detail_id__booking_order_id=booking_order.id,
                delete_mark=0,
                enabled_mark=1,
                allocation_status__in=[1, 2]  # 已分配或已上刊
            ).select_related(
                'resource_id__base_media_type_id',
                'booking_detail_id__media_type_id',
                'roadline_id',
                'roadline_company_id',
                'vehicle_id'
            )
            
            if not positions.exists():
                return ErrorResponse(
                    msg="该预订单没有分配车位，无法创建上刊订单明细",
                    code=400
                )
            
            # 6. 为每个车位广告创建上刊订单明细
            created_detail_count = 0
            failed_positions = []
            
            for position in positions:
                try:
                    # 检查resource_id是否存在
                    if not position.resource_id:
                        failed_positions.append({
                            'position_id': position.id,
                            'reason': '车位广告缺少资源位信息'
                        })
                        continue
                    
                    # 获取基础媒体类型（从resource_id获取）
                    base_media_type = position.resource_id.base_media_type_id
                    if not base_media_type:
                        failed_positions.append({
                            'position_id': position.id,
                            'reason': '资源位缺少基础媒体类型信息'
                        })
                        continue
                    
                    # 获取组合媒体类型（从booking_detail_id获取，如果是组合类型）
                    booking_detail = position.booking_detail_id
                    composite_media_type = None
                    composite_media_type_name = None
                    
                    if booking_detail and booking_detail.is_composite and booking_detail.media_type_id:
                        composite_media_type = booking_detail.media_type_id
                        composite_media_type_name = booking_detail.media_type_name or ''
                    
                    # 确保必要的关联对象存在
                    if not position.roadline_id:
                        failed_positions.append({
                            'position_id': position.id,
                            'reason': '车位广告缺少线路信息'
                        })
                        continue
                    
                    if not position.roadline_company_id:
                        failed_positions.append({
                            'position_id': position.id,
                            'reason': '车位广告缺少营运公司信息'
                        })
                        continue
                    
                    # 创建上刊订单明细
                    detail_data = {
                        'order_id': on_air_order.id,
                        'position_id': position.id,
                        'roadline_id': position.roadline_id.id,
                        'roadline_name': position.roadline_name or '',
                        'roadline_company_id': position.roadline_company_id.id,
                        'roadline_company_name': position.roadline_company_name or '',
                        'plan_vehicle_id': position.vehicle_id.id if position.vehicle_id else None,
                        'plan_vehicle_no': position.vehicle_no or '',
                        'composite_media_type_id': composite_media_type.id if composite_media_type else None,
                        'composite_media_type_name': composite_media_type_name or '',
                        'base_media_type_id': base_media_type.id,
                        'base_media_type_name': base_media_type.media_name or '',
                        'execution_status': 1,  # 待执行
                        # 不手动传递creator，让序列化器自动从request中获取
                    }
                    
                    # 传递request上下文，让序列化器自动填充creator等审计字段
                    detail_serializer = OnAirOrderDetailModelCreateSerializer(
                        data=detail_data,
                        context={'request': request}
                    )
                    detail_serializer.is_valid(raise_exception=True)
                    detail_serializer.save()
                    created_detail_count += 1
                    
                except Exception as e:
                    # 记录错误但继续处理其他明细
                    import traceback
                    error_detail = traceback.format_exc()
                    print(f"[审核通过] 创建上刊订单明细失败: position_id={position.id}, error={str(e)}")
                    print(f"[审核通过] 错误详情: {error_detail}")
                    failed_positions.append({
                        'position_id': position.id,
                        'reason': f'创建明细时发生异常: {str(e)}'
                    })
                    continue
            
            if created_detail_count == 0:
                # 如果所有明细都创建失败，回滚上刊订单主表
                on_air_order.delete()
                error_msg = "创建上刊订单明细失败，请检查车位广告数据"
                if failed_positions:
                    failed_details = []
                    for p in failed_positions[:5]:
                        failed_details.append(f"车位ID:{p['position_id']}-{p['reason']}")
                    error_msg += f"\n失败详情：{', '.join(failed_details)}"
                return ErrorResponse(
                    msg=error_msg,
                    code=500
                )
            
            # 构建返回消息
            msg = f"审核通过！已创建上刊订单（订单号：{on_air_order.order_no}），共 {created_detail_count} 条明细"
            if failed_positions:
                msg += f"，{len(failed_positions)} 条明细创建失败"
            
            return SuccessResponse(
                data={
                    'on_air_order_id': str(on_air_order.id),
                    'on_air_order_no': on_air_order.order_no,
                    'created_detail_count': created_detail_count,
                    'failed_count': len(failed_positions),
                    'failed_positions': failed_positions[:10] if failed_positions else [],  # 最多返回10条失败记录
                },
                msg=msg
            )
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"[审核通过] 异常详情: {error_detail}")
            return ErrorResponse(
                msg=f"审核通过失败: {str(e)}",
                code=500
            )

