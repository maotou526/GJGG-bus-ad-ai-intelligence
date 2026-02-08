'''
Description: 预订订单视图
Version: 2.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors:
LastEditTime: 2026-02-08
'''
from typing import List, Dict
from rest_framework.decorators import action
from rest_framework import status
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

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
from dvadmin_twodev.booking_manage.vehicle_ad_position_change.models import VehicleAdPositionChangeModel
from dvadmin_twodev.basedata.vehicle_ad_resource.models import VehicleAdResourceModel
from dvadmin_twodev.basedata.vehicle.models import VehicleModel
from dvadmin_twodev.basedata.media_type.models import AdMediaTypeModel
from dvadmin_twodev.basedata.media_type_composition.models import AdMediaTypeCompositionModel

# ==================== 状态常量 ====================
# 预订单状态
STATUS_DRAFT = 1              # 草稿
STATUS_MEDIA_FIRST = 2        # 待媒体部初审
STATUS_COMPANY_REVIEW = 3     # 待营运公司审核
STATUS_MEDIA_FINAL = 4        # 待媒体部复审
STATUS_APPROVED = 5           # 已通过
STATUS_COMPLETED = 6          # 已完成
STATUS_REJECTED = 7           # 已驳回
STATUS_CANCELLED = 8          # 已取消

# 审批节点
NODE_MEDIA_FIRST = 1          # 媒体部初审
NODE_COMPANY_REVIEW = 2       # 营运公司审核
NODE_MEDIA_FINAL = 3          # 媒体部复审

# 车位确认状态
CONFIRM_PENDING = 1           # 待确认
CONFIRM_CONFIRMED = 2         # 已确认
CONFIRM_EXCLUDED = 3          # 已剔除


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
        'booking_type', 'booking_status', 'current_approval_node',
        'original_booking_id',
        'start_date', 'end_date', 'enabled_mark', 'delete_mark'
    ]

    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        'id', 'booking_no', 'customer_id', 'customer_name',
        'booking_type', 'booking_status', 'current_approval_node',
        'original_booking_id',
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
    
    # ==================== 审批流程接口 ====================

    @action(detail=True, methods=['post'], url_path='submit')
    @transaction.atomic
    def submit(self, request, pk=None):
        """
        提交预订单进入审批流程
        草稿(1) → 待媒体部初审(2)

        POST /api/BookingOrderModelViewSet/{id}/submit/
        """
        booking_order = self.get_object()

        if booking_order.booking_status != STATUS_DRAFT:
            return ErrorResponse(msg="只有草稿状态的预订单才能提交审批", code=400)

        # 检查是否有明细
        details = BookingOrderDetailModel.objects.filter(
            booking_order_id=booking_order.id, delete_mark=0, enabled_mark=1
        )
        if not details.exists():
            return ErrorResponse(msg="预订单没有明细数据，无法提交", code=400)

        # 执行车位分配
        result = self._allocate_positions_for_order(booking_order.id)
        if not result['success']:
            error_details = [f.get('reason', '未知错误') for f in result.get('failed_details', [])]
            return ErrorResponse(
                msg=f"车位分配失败，无法提交审批。\n\n{''.join(error_details)}",
                code=400
            )

        # 更新状态
        booking_order.booking_status = STATUS_MEDIA_FIRST
        booking_order.current_approval_node = NODE_MEDIA_FIRST
        booking_order.submitter_id = request.user
        booking_order.submit_time = timezone.now()
        # 清除可能的驳回信息
        booking_order.reject_reason = None
        booking_order.reject_node = None
        booking_order.reject_user_id = None
        booking_order.reject_time = None
        booking_order.save()

        return SuccessResponse(
            data={'id': str(booking_order.id), 'booking_status': STATUS_MEDIA_FIRST, 'allocation_result': result},
            msg=f"提交成功，{result['message']}，等待媒体部初审"
        )

    @action(detail=True, methods=['post'], url_path='first_review_approve')
    @transaction.atomic
    def first_review_approve(self, request, pk=None):
        """
        媒体部初审通过
        待媒体部初审(2) → 待营运公司审核(3)

        POST /api/BookingOrderModelViewSet/{id}/first_review_approve/
        请求体: {"review_comment": "审核意见"}
        """
        booking_order = self.get_object()

        if booking_order.booking_status != STATUS_MEDIA_FIRST:
            return ErrorResponse(msg="当前状态不是待媒体部初审，无法操作", code=400)

        review_comment = request.data.get('review_comment', '')

        # 重置所有车位的确认状态为"待确认"
        positions = VehicleAdPositionModel.objects.filter(
            booking_detail_id__booking_order_id=booking_order.id,
            delete_mark=0, enabled_mark=1, allocation_status=1
        )
        positions.update(confirm_status=CONFIRM_PENDING, confirm_user_id=None, confirm_time=None, exclude_reason=None)

        # 更新订单状态
        booking_order.booking_status = STATUS_COMPANY_REVIEW
        booking_order.current_approval_node = NODE_COMPANY_REVIEW
        if review_comment:
            booking_order.remark = (booking_order.remark or '') + f"\n[媒体部初审意见] {review_comment}"
        booking_order.save()

        return SuccessResponse(
            data={'id': str(booking_order.id), 'booking_status': STATUS_COMPANY_REVIEW},
            msg="媒体部初审通过，已转营运公司审核"
        )

    @action(detail=True, methods=['post'], url_path='first_review_reject')
    @transaction.atomic
    def first_review_reject(self, request, pk=None):
        """
        媒体部初审驳回
        待媒体部初审(2) → 已驳回(7)

        POST /api/BookingOrderModelViewSet/{id}/first_review_reject/
        请求体: {"reject_reason": "驳回原因"}（必填）
        """
        booking_order = self.get_object()

        if booking_order.booking_status != STATUS_MEDIA_FIRST:
            return ErrorResponse(msg="当前状态不是待媒体部初审，无法驳回", code=400)

        reject_reason = request.data.get('reject_reason', '')
        if not reject_reason:
            return ErrorResponse(msg="驳回原因不能为空", code=400)

        # 释放车位
        self._release_positions_for_order(booking_order.id)

        # 更新状态
        booking_order.booking_status = STATUS_REJECTED
        booking_order.current_approval_node = None
        booking_order.reject_reason = reject_reason
        booking_order.reject_node = NODE_MEDIA_FIRST
        booking_order.reject_user_id = request.user
        booking_order.reject_time = timezone.now()
        booking_order.save()

        return SuccessResponse(
            data={'id': str(booking_order.id), 'booking_status': STATUS_REJECTED},
            msg="已驳回"
        )

    @action(detail=True, methods=['post'], url_path='company_confirm_position')
    @transaction.atomic
    def company_confirm_position(self, request, pk=None):
        """
        营运公司确认单个车位

        POST /api/BookingOrderModelViewSet/{id}/company_confirm_position/
        请求体: {"position_id": "uuid"}
        """
        booking_order = self.get_object()

        if booking_order.booking_status != STATUS_COMPANY_REVIEW:
            return ErrorResponse(msg="当前状态不是待营运公司审核，无法操作", code=400)

        position_id = request.data.get('position_id')
        if not position_id:
            return ErrorResponse(msg="position_id 不能为空", code=400)

        try:
            position = VehicleAdPositionModel.objects.get(
                id=position_id,
                booking_detail_id__booking_order_id=booking_order.id,
                delete_mark=0, enabled_mark=1
            )
        except VehicleAdPositionModel.DoesNotExist:
            return ErrorResponse(msg="车位记录不存在或不属于该预订单", code=404)

        if position.confirm_status != CONFIRM_PENDING:
            return ErrorResponse(msg="该车位已经处理过，无法重复操作", code=400)

        position.confirm_status = CONFIRM_CONFIRMED
        position.confirm_user_id = request.user
        position.confirm_time = timezone.now()
        position.save()

        return SuccessResponse(
            data={'position_id': str(position.id), 'confirm_status': CONFIRM_CONFIRMED},
            msg="车位已确认"
        )

    @action(detail=True, methods=['post'], url_path='company_exclude_position')
    @transaction.atomic
    def company_exclude_position(self, request, pk=None):
        """
        营运公司剔除车位

        POST /api/BookingOrderModelViewSet/{id}/company_exclude_position/
        请求体: {"position_id": "uuid", "exclude_reason": "剔除原因"}（原因必填）
        """
        booking_order = self.get_object()

        if booking_order.booking_status != STATUS_COMPANY_REVIEW:
            return ErrorResponse(msg="当前状态不是待营运公司审核，无法操作", code=400)

        position_id = request.data.get('position_id')
        exclude_reason = request.data.get('exclude_reason', '')

        if not position_id:
            return ErrorResponse(msg="position_id 不能为空", code=400)
        if not exclude_reason:
            return ErrorResponse(msg="剔除原因不能为空", code=400)

        try:
            position = VehicleAdPositionModel.objects.get(
                id=position_id,
                booking_detail_id__booking_order_id=booking_order.id,
                delete_mark=0, enabled_mark=1
            )
        except VehicleAdPositionModel.DoesNotExist:
            return ErrorResponse(msg="车位记录不存在或不属于该预订单", code=404)

        if position.confirm_status == CONFIRM_EXCLUDED:
            return ErrorResponse(msg="该车位已剔除，无法重复操作", code=400)

        # 记录变更历史
        import json
        before_data = {
            'vehicle_id': str(position.vehicle_id_id),
            'vehicle_no': position.vehicle_no,
            'confirm_status': position.confirm_status,
        }

        position.confirm_status = CONFIRM_EXCLUDED
        position.exclude_reason = exclude_reason
        position.confirm_user_id = request.user
        position.confirm_time = timezone.now()
        position.allocation_status = 4  # 已取消
        position.save()

        # 释放对应资源位
        if position.resource_id:
            resource = position.resource_id
            resource.resource_status = 1  # 空闲
            resource.save()

        after_data = {
            'vehicle_id': str(position.vehicle_id_id),
            'vehicle_no': position.vehicle_no,
            'confirm_status': CONFIRM_EXCLUDED,
            'exclude_reason': exclude_reason,
        }

        VehicleAdPositionChangeModel.objects.create(
            booking_order_id=booking_order,
            booking_detail_id=position.booking_detail_id,
            action_type=2,  # 删除车位
            position_id=position,
            roadline_id=position.roadline_id,
            roadline_name=position.roadline_name,
            roadline_company_id=position.roadline_company_id,
            roadline_company_name=position.roadline_company_name,
            vehicle_id=position.vehicle_id,
            vehicle_no=position.vehicle_no,
            resource_id=position.resource_id,
            before_data=json.dumps(before_data, ensure_ascii=False),
            after_data=json.dumps(after_data, ensure_ascii=False),
            change_reason=f"营运公司剔除：{exclude_reason}",
            change_node=str(NODE_COMPANY_REVIEW),
            operator_id=request.user,
            operation_time=timezone.now(),
        )

        return SuccessResponse(
            data={'position_id': str(position.id), 'confirm_status': CONFIRM_EXCLUDED},
            msg="车位已剔除"
        )

    @action(detail=True, methods=['post'], url_path='company_swap_vehicle')
    @transaction.atomic
    def company_swap_vehicle(self, request, pk=None):
        """
        营运公司换车（替换某个车位的车辆）

        POST /api/BookingOrderModelViewSet/{id}/company_swap_vehicle/
        请求体: {"position_id": "uuid", "new_vehicle_id": "uuid", "swap_reason": "换车原因"}
        """
        booking_order = self.get_object()

        if booking_order.booking_status != STATUS_COMPANY_REVIEW:
            return ErrorResponse(msg="当前状态不是待营运公司审核，无法操作", code=400)

        position_id = request.data.get('position_id')
        new_vehicle_id = request.data.get('new_vehicle_id')
        swap_reason = request.data.get('swap_reason', '营运公司换车')

        if not position_id or not new_vehicle_id:
            return ErrorResponse(msg="position_id 和 new_vehicle_id 不能为空", code=400)

        try:
            position = VehicleAdPositionModel.objects.get(
                id=position_id,
                booking_detail_id__booking_order_id=booking_order.id,
                delete_mark=0, enabled_mark=1
            )
        except VehicleAdPositionModel.DoesNotExist:
            return ErrorResponse(msg="车位记录不存在或不属于该预订单", code=404)

        try:
            new_vehicle = VehicleModel.objects.get(id=new_vehicle_id, delete_mark=0, enabled_mark=1)
        except VehicleModel.DoesNotExist:
            return ErrorResponse(msg="新车辆不存在", code=404)

        # 冲突检测：检查新车辆在该时间段是否有冲突
        base_media_type_id = position.resource_id.base_media_type_id if position.resource_id else None
        if base_media_type_id:
            conflicts = VehicleAdPositionModel.objects.filter(
                vehicle_id=new_vehicle,
                resource_id__base_media_type_id=base_media_type_id,
                delete_mark=0, enabled_mark=1,
                allocation_status__in=[1, 2],
            ).filter(
                Q(reserved_start_date__lte=position.reserved_end_date) &
                Q(reserved_end_date__gte=position.reserved_start_date)
            ).exclude(id=position.id)

            if conflicts.exists():
                return ErrorResponse(msg="新车辆在该时间段已有其他广告分配，存在冲突", code=400)

        # 记录变更前数据
        import json
        before_data = {
            'vehicle_id': str(position.vehicle_id_id),
            'vehicle_no': position.vehicle_no,
        }

        # 释放旧资源位
        old_resource = position.resource_id
        if old_resource:
            old_resource.resource_status = 1  # 空闲
            old_resource.save()

        # 创建新资源位
        new_resource = self._get_or_create_resource(
            vehicle_id=new_vehicle.id,
            base_media_type_id=base_media_type_id.id if hasattr(base_media_type_id, 'id') else base_media_type_id,
            start_date=position.reserved_start_date,
            end_date=position.reserved_end_date
        )
        new_resource.resource_status = 2  # 预订
        new_resource.save()

        # 更新车位记录
        position.vehicle_id = new_vehicle
        position.vehicle_no = new_vehicle.vehicle_no
        position.resource_id = new_resource
        position.confirm_status = CONFIRM_CONFIRMED
        position.confirm_user_id = request.user
        position.confirm_time = timezone.now()
        position.save()

        after_data = {
            'vehicle_id': str(new_vehicle.id),
            'vehicle_no': new_vehicle.vehicle_no,
        }

        # 记录变更历史
        VehicleAdPositionChangeModel.objects.create(
            booking_order_id=booking_order,
            booking_detail_id=position.booking_detail_id,
            action_type=3,  # 修改车位
            position_id=position,
            roadline_id=position.roadline_id,
            roadline_name=position.roadline_name,
            roadline_company_id=position.roadline_company_id,
            roadline_company_name=position.roadline_company_name,
            vehicle_id=new_vehicle,
            vehicle_no=new_vehicle.vehicle_no,
            resource_id=new_resource,
            before_data=json.dumps(before_data, ensure_ascii=False),
            after_data=json.dumps(after_data, ensure_ascii=False),
            change_reason=f"营运公司换车：{swap_reason}",
            change_node=str(NODE_COMPANY_REVIEW),
            operator_id=request.user,
            operation_time=timezone.now(),
        )

        return SuccessResponse(
            data={'position_id': str(position.id), 'new_vehicle_no': new_vehicle.vehicle_no},
            msg=f"换车成功：{before_data['vehicle_no']} → {new_vehicle.vehicle_no}"
        )

    @action(detail=True, methods=['post'], url_path='company_batch_confirm')
    @transaction.atomic
    def company_batch_confirm(self, request, pk=None):
        """
        营运公司批量确认（确认该公司所有待确认车位）

        POST /api/BookingOrderModelViewSet/{id}/company_batch_confirm/
        请求体: {"company_id": "uuid"}（可选，不传则确认全部待确认车位）
        """
        booking_order = self.get_object()

        if booking_order.booking_status != STATUS_COMPANY_REVIEW:
            return ErrorResponse(msg="当前状态不是待营运公司审核，无法操作", code=400)

        company_id = request.data.get('company_id')
        positions = VehicleAdPositionModel.objects.filter(
            booking_detail_id__booking_order_id=booking_order.id,
            delete_mark=0, enabled_mark=1,
            confirm_status=CONFIRM_PENDING
        )

        if company_id:
            positions = positions.filter(roadline_company_id=company_id)

        count = positions.update(
            confirm_status=CONFIRM_CONFIRMED,
            confirm_user_id=request.user,
            confirm_time=timezone.now()
        )

        return SuccessResponse(
            data={'confirmed_count': count},
            msg=f"批量确认成功，共确认 {count} 个车位"
        )

    @action(detail=True, methods=['post'], url_path='company_review_complete')
    @transaction.atomic
    def company_review_complete(self, request, pk=None):
        """
        营运公司审核完成（所有车位都已确认/剔除后可触发）
        待营运公司审核(3) → 待媒体部复审(4)

        POST /api/BookingOrderModelViewSet/{id}/company_review_complete/
        请求体: {"review_comment": "审核意见"}
        """
        booking_order = self.get_object()

        if booking_order.booking_status != STATUS_COMPANY_REVIEW:
            return ErrorResponse(msg="当前状态不是待营运公司审核，无法操作", code=400)

        # 检查是否还有待确认的车位
        pending_count = VehicleAdPositionModel.objects.filter(
            booking_detail_id__booking_order_id=booking_order.id,
            delete_mark=0, enabled_mark=1,
            allocation_status=1,  # 已分配
            confirm_status=CONFIRM_PENDING
        ).count()

        if pending_count > 0:
            return ErrorResponse(msg=f"还有 {pending_count} 个车位未处理（确认/剔除），无法完成审核", code=400)

        review_comment = request.data.get('review_comment', '')

        booking_order.booking_status = STATUS_MEDIA_FINAL
        booking_order.current_approval_node = NODE_MEDIA_FINAL
        if review_comment:
            booking_order.remark = (booking_order.remark or '') + f"\n[营运公司审核意见] {review_comment}"
        booking_order.save()

        return SuccessResponse(
            data={'id': str(booking_order.id), 'booking_status': STATUS_MEDIA_FINAL},
            msg="营运公司审核完成，已转媒体部复审"
        )

    @action(detail=True, methods=['post'], url_path='final_review_approve')
    @transaction.atomic
    def final_review_approve(self, request, pk=None):
        """
        媒体部复审通过（创建上刊订单）
        待媒体部复审(4) → 已通过(5)

        POST /api/BookingOrderModelViewSet/{id}/final_review_approve/
        请求体: {"review_comment": "审核意见"}
        """
        booking_order = self.get_object()

        if booking_order.booking_status != STATUS_MEDIA_FINAL:
            return ErrorResponse(msg="当前状态不是待媒体部复审，无法操作", code=400)

        review_comment = request.data.get('review_comment', '')

        # 更新状态
        booking_order.booking_status = STATUS_APPROVED
        booking_order.current_approval_node = None
        booking_order.approved_time = timezone.now()
        if review_comment:
            booking_order.remark = (booking_order.remark or '') + f"\n[媒体部复审意见] {review_comment}"
        booking_order.save()

        # 创建上刊订单
        on_air_result = self._create_on_air_order(booking_order, request)

        msg = "媒体部复审通过"
        if on_air_result.get('success'):
            msg += f"，已创建上刊订单（{on_air_result.get('order_no', '')}）"

        return SuccessResponse(
            data={
                'id': str(booking_order.id),
                'booking_status': STATUS_APPROVED,
                'on_air_result': on_air_result
            },
            msg=msg
        )

    @action(detail=True, methods=['post'], url_path='final_review_reject')
    @transaction.atomic
    def final_review_reject(self, request, pk=None):
        """
        媒体部复审驳回
        待媒体部复审(4) → 已驳回(7)

        POST /api/BookingOrderModelViewSet/{id}/final_review_reject/
        请求体: {"reject_reason": "驳回原因"}（必填）
        """
        booking_order = self.get_object()

        if booking_order.booking_status != STATUS_MEDIA_FINAL:
            return ErrorResponse(msg="当前状态不是待媒体部复审，无法驳回", code=400)

        reject_reason = request.data.get('reject_reason', '')
        if not reject_reason:
            return ErrorResponse(msg="驳回原因不能为空", code=400)

        # 释放车位
        self._release_positions_for_order(booking_order.id)

        booking_order.booking_status = STATUS_REJECTED
        booking_order.current_approval_node = None
        booking_order.reject_reason = reject_reason
        booking_order.reject_node = NODE_MEDIA_FINAL
        booking_order.reject_user_id = request.user
        booking_order.reject_time = timezone.now()
        booking_order.save()

        return SuccessResponse(
            data={'id': str(booking_order.id), 'booking_status': STATUS_REJECTED},
            msg="已驳回"
        )

    @action(detail=True, methods=['post'], url_path='resubmit')
    @transaction.atomic
    def resubmit(self, request, pk=None):
        """
        驳回后重新发起（基于被驳回的订单创建新订单）
        已驳回(7) → 草稿(1)

        POST /api/BookingOrderModelViewSet/{id}/resubmit/
        """
        original_order = self.get_object()

        if original_order.booking_status != STATUS_REJECTED:
            return ErrorResponse(msg="只有已驳回的预订单才能重新发起", code=400)

        from datetime import datetime
        import random

        # 生成新订单号
        date_str = datetime.now().strftime('%Y%m%d')
        while True:
            random_str = str(random.randint(1000, 9999))
            new_booking_no = f"BK-{date_str}-{random_str}"
            if not BookingOrderModel.objects.filter(booking_no=new_booking_no).exists():
                break

        # 创建新订单（复制原订单数据）
        new_order = BookingOrderModel.objects.create(
            booking_no=new_booking_no,
            customer_id=original_order.customer_id,
            customer_name=original_order.customer_name,
            booking_type=4,  # 重新发起
            original_booking_id=original_order,
            booking_status=STATUS_DRAFT,
            current_approval_node=None,
            ad_content=original_order.ad_content,
            start_date=original_order.start_date,
            end_date=original_order.end_date,
            total_amount=original_order.total_amount,
            remark=f"重新发起自：{original_order.booking_no}",
            creator=request.user,
            creator_name=request.user.name if hasattr(request.user, 'name') else str(request.user),
        )

        # 复制明细数据
        original_details = BookingOrderDetailModel.objects.filter(
            booking_order_id=original_order.id, delete_mark=0, enabled_mark=1
        )

        for detail in original_details:
            BookingOrderDetailModel.objects.create(
                booking_order_id=new_order,
                roadline_id=detail.roadline_id,
                roadline_name=detail.roadline_name,
                roadline_company_id=detail.roadline_company_id,
                roadline_company_name=detail.roadline_company_name,
                media_type_id=detail.media_type_id,
                media_type_name=detail.media_type_name,
                is_composite=detail.is_composite,
                quantity=detail.quantity,
                unit_price=detail.unit_price,
                subtotal_amount=detail.subtotal_amount,
                start_date=detail.start_date,
                end_date=detail.end_date,
                lock_status=1,  # 未锁定
                creator=request.user,
                creator_name=request.user.name if hasattr(request.user, 'name') else str(request.user),
            )

        return SuccessResponse(
            data={
                'id': str(new_order.id),
                'booking_no': new_order.booking_no,
                'original_booking_no': original_order.booking_no,
            },
            msg=f"重新发起成功，新订单号：{new_order.booking_no}，请编辑后提交审批"
        )

    @action(detail=True, methods=['post'], url_path='cancel')
    @transaction.atomic
    def cancel(self, request, pk=None):
        """
        取消预订单

        POST /api/BookingOrderModelViewSet/{id}/cancel/
        请求体: {"cancel_reason": "取消原因"}
        """
        booking_order = self.get_object()

        if booking_order.booking_status in [STATUS_APPROVED, STATUS_COMPLETED, STATUS_CANCELLED]:
            return ErrorResponse(msg="已通过/已完成/已取消的订单无法取消", code=400)

        cancel_reason = request.data.get('cancel_reason', '')

        # 释放车位
        if booking_order.booking_status in [STATUS_MEDIA_FIRST, STATUS_COMPANY_REVIEW, STATUS_MEDIA_FINAL]:
            self._release_positions_for_order(booking_order.id)

        booking_order.booking_status = STATUS_CANCELLED
        booking_order.current_approval_node = None
        if cancel_reason:
            booking_order.remark = (booking_order.remark or '') + f"\n[取消原因] {cancel_reason}"
        booking_order.save()

        return SuccessResponse(
            data={'id': str(booking_order.id), 'booking_status': STATUS_CANCELLED},
            msg="预订单已取消"
        )

    @action(detail=True, methods=['get'], url_path='get_available_actions')
    def get_available_actions(self, request, pk=None):
        """
        获取当前用户对该预订单可执行的操作列表

        GET /api/BookingOrderModelViewSet/{id}/get_available_actions/

        返回按照 booking_status 和 current_approval_node 可执行的操作：
        - edit: 编辑
        - submit: 提交审批
        - first_review_approve: 媒体部初审通过
        - first_review_reject: 媒体部初审驳回
        - company_confirm: 营运公司确认/剔除/换车
        - company_review_complete: 营运公司审核完成
        - final_review_approve: 媒体部复审通过
        - final_review_reject: 媒体部复审驳回
        - resubmit: 重新发起
        - cancel: 取消
        """
        booking_order = self.get_object()
        actions = []
        bs = booking_order.booking_status

        if bs == STATUS_DRAFT:
            actions.extend(['edit', 'submit', 'cancel'])
        elif bs == STATUS_MEDIA_FIRST:
            actions.extend(['first_review_approve', 'first_review_reject', 'cancel'])
        elif bs == STATUS_COMPANY_REVIEW:
            actions.extend(['company_confirm', 'company_review_complete', 'cancel'])
        elif bs == STATUS_MEDIA_FINAL:
            actions.extend(['final_review_approve', 'final_review_reject', 'cancel'])
        elif bs == STATUS_REJECTED:
            actions.extend(['resubmit'])

        # 获取审批进度统计
        stats = {}
        if bs == STATUS_COMPANY_REVIEW:
            all_positions = VehicleAdPositionModel.objects.filter(
                booking_detail_id__booking_order_id=booking_order.id,
                delete_mark=0, enabled_mark=1, allocation_status=1
            )
            stats = {
                'total': all_positions.count(),
                'confirmed': all_positions.filter(confirm_status=CONFIRM_CONFIRMED).count(),
                'excluded': all_positions.filter(confirm_status=CONFIRM_EXCLUDED).count(),
                'pending': all_positions.filter(confirm_status=CONFIRM_PENDING).count(),
            }

        return SuccessResponse(
            data={
                'id': str(booking_order.id),
                'booking_status': bs,
                'current_approval_node': booking_order.current_approval_node,
                'actions': actions,
                'position_stats': stats,
            }
        )

    @action(detail=True, methods=['post'], url_path='review_add_position')
    @transaction.atomic
    def review_add_position(self, request, pk=None):
        """
        审批过程中新增车位（媒体部初审/复审可操作）

        POST /api/BookingOrderModelViewSet/{id}/review_add_position/
        请求体: {
            "booking_detail_id": "uuid",
            "vehicle_id": "uuid",
            "reason": "新增原因"
        }
        """
        booking_order = self.get_object()

        if booking_order.booking_status not in [STATUS_MEDIA_FIRST, STATUS_MEDIA_FINAL]:
            return ErrorResponse(msg="只有媒体部初审/复审阶段可以新增车位", code=400)

        detail_id = request.data.get('booking_detail_id')
        vehicle_id = request.data.get('vehicle_id')
        reason = request.data.get('reason', '审批中新增')

        if not detail_id or not vehicle_id:
            return ErrorResponse(msg="booking_detail_id 和 vehicle_id 不能为空", code=400)

        try:
            detail = BookingOrderDetailModel.objects.get(
                id=detail_id, booking_order_id=booking_order.id, delete_mark=0
            )
        except BookingOrderDetailModel.DoesNotExist:
            return ErrorResponse(msg="明细不存在", code=404)

        try:
            vehicle = VehicleModel.objects.get(id=vehicle_id, delete_mark=0, enabled_mark=1)
        except VehicleModel.DoesNotExist:
            return ErrorResponse(msg="车辆不存在", code=404)

        # 确定基础媒体类型
        if detail.is_composite:
            compositions = AdMediaTypeCompositionModel.objects.filter(
                composite_type_id=detail.media_type_id.id, delete_mark=0, enabled_mark=1
            )
            base_types = AdMediaTypeModel.objects.filter(
                id__in=[c.component_type_id for c in compositions], delete_mark=0, enabled_mark=1
            )
        else:
            base_types = [detail.media_type_id]

        # 冲突检测
        for bt in base_types:
            bt_id = bt.id if hasattr(bt, 'id') else bt
            conflicts = VehicleAdPositionModel.objects.filter(
                vehicle_id=vehicle,
                resource_id__base_media_type_id=bt_id,
                delete_mark=0, enabled_mark=1,
                allocation_status__in=[1, 2],
            ).filter(
                Q(reserved_start_date__lte=detail.end_date) &
                Q(reserved_end_date__gte=detail.start_date)
            )
            if conflicts.exists():
                return ErrorResponse(
                    msg=f"车辆 {vehicle.vehicle_no} 在该时间段的 {bt.media_name if hasattr(bt, 'media_name') else bt_id} 资源位已有冲突",
                    code=400
                )

        # 创建车位记录
        import json
        created_positions = []
        for bt in base_types:
            bt_id = bt.id if hasattr(bt, 'id') else bt
            resource = self._get_or_create_resource(
                vehicle_id=vehicle.id, base_media_type_id=bt_id,
                start_date=detail.start_date, end_date=detail.end_date
            )
            resource.resource_status = 2
            resource.save()

            position = VehicleAdPositionModel.objects.create(
                booking_detail_id=detail,
                roadline_id=detail.roadline_id,
                roadline_name=detail.roadline_name,
                roadline_company_id=detail.roadline_company_id,
                roadline_company_name=detail.roadline_company_name,
                resource_id=resource,
                vehicle_id=vehicle,
                vehicle_no=vehicle.vehicle_no,
                media_type_id=detail.media_type_id,
                media_type_name=detail.media_type_name,
                reserved_start_date=detail.start_date,
                reserved_end_date=detail.end_date,
                allocation_status=1,
                confirm_status=CONFIRM_PENDING,
                creator=request.user,
                creator_name=request.user.name if hasattr(request.user, 'name') else str(request.user),
            )
            created_positions.append(position)

        # 记录变更
        change_node = str(NODE_MEDIA_FIRST) if booking_order.booking_status == STATUS_MEDIA_FIRST else str(NODE_MEDIA_FINAL)
        for pos in created_positions:
            VehicleAdPositionChangeModel.objects.create(
                booking_order_id=booking_order,
                booking_detail_id=detail,
                action_type=1,  # 新增
                position_id=pos,
                roadline_id=pos.roadline_id,
                roadline_name=pos.roadline_name,
                roadline_company_id=pos.roadline_company_id,
                roadline_company_name=pos.roadline_company_name,
                vehicle_id=vehicle,
                vehicle_no=vehicle.vehicle_no,
                resource_id=pos.resource_id,
                after_data=json.dumps({'vehicle_no': vehicle.vehicle_no}, ensure_ascii=False),
                change_reason=reason,
                change_node=change_node,
                operator_id=request.user,
                operation_time=timezone.now(),
            )

        return SuccessResponse(
            data={'created_count': len(created_positions)},
            msg=f"成功新增 {len(created_positions)} 个车位"
        )

    @action(detail=True, methods=['post'], url_path='review_remove_position')
    @transaction.atomic
    def review_remove_position(self, request, pk=None):
        """
        审批过程中删除车位（媒体部初审/复审可操作）

        POST /api/BookingOrderModelViewSet/{id}/review_remove_position/
        请求体: {"position_id": "uuid", "reason": "删除原因"}
        """
        booking_order = self.get_object()

        if booking_order.booking_status not in [STATUS_MEDIA_FIRST, STATUS_MEDIA_FINAL]:
            return ErrorResponse(msg="只有媒体部初审/复审阶段可以删除车位", code=400)

        position_id = request.data.get('position_id')
        reason = request.data.get('reason', '审批中删除')

        if not position_id:
            return ErrorResponse(msg="position_id 不能为空", code=400)

        try:
            position = VehicleAdPositionModel.objects.get(
                id=position_id,
                booking_detail_id__booking_order_id=booking_order.id,
                delete_mark=0, enabled_mark=1
            )
        except VehicleAdPositionModel.DoesNotExist:
            return ErrorResponse(msg="车位记录不存在", code=404)

        import json
        before_data = {
            'vehicle_id': str(position.vehicle_id_id),
            'vehicle_no': position.vehicle_no,
        }

        # 释放资源位
        if position.resource_id:
            position.resource_id.resource_status = 1
            position.resource_id.save()

        # 软删除车位
        position.delete_mark = 1
        position.allocation_status = 4
        position.save()

        change_node = str(NODE_MEDIA_FIRST) if booking_order.booking_status == STATUS_MEDIA_FIRST else str(NODE_MEDIA_FINAL)
        VehicleAdPositionChangeModel.objects.create(
            booking_order_id=booking_order,
            booking_detail_id=position.booking_detail_id,
            action_type=2,
            position_id=position,
            roadline_id=position.roadline_id,
            roadline_name=position.roadline_name,
            roadline_company_id=position.roadline_company_id,
            roadline_company_name=position.roadline_company_name,
            vehicle_id=position.vehicle_id,
            vehicle_no=position.vehicle_no,
            resource_id=position.resource_id,
            before_data=json.dumps(before_data, ensure_ascii=False),
            change_reason=reason,
            change_node=change_node,
            operator_id=request.user,
            operation_time=timezone.now(),
        )

        return SuccessResponse(
            data={'position_id': str(position.id)},
            msg="车位已删除"
        )

    @action(detail=True, methods=['get'], url_path='get_positions_by_company')
    def get_positions_by_company(self, request, pk=None):
        """
        按营运公司分组获取车位列表（营运公司审核页面使用）

        GET /api/BookingOrderModelViewSet/{id}/get_positions_by_company/
        """
        booking_order = self.get_object()

        positions = VehicleAdPositionModel.objects.filter(
            booking_detail_id__booking_order_id=booking_order.id,
            delete_mark=0, enabled_mark=1, allocation_status=1
        ).select_related('roadline_id', 'roadline_company_id', 'vehicle_id', 'resource_id')

        from dvadmin_twodev.booking_manage.vehicle_ad_position.serializers import VehicleAdPositionModelListSerializer

        # 按营运公司分组
        company_groups = {}
        for pos in positions:
            company_id = str(pos.roadline_company_id_id) if pos.roadline_company_id else 'unknown'
            company_name = pos.roadline_company_name or '未知公司'
            if company_id not in company_groups:
                company_groups[company_id] = {
                    'company_id': company_id,
                    'company_name': company_name,
                    'positions': [],
                    'stats': {'total': 0, 'confirmed': 0, 'excluded': 0, 'pending': 0},
                }
            group = company_groups[company_id]
            group['positions'].append(VehicleAdPositionModelListSerializer(pos).data)
            group['stats']['total'] += 1
            if pos.confirm_status == CONFIRM_CONFIRMED:
                group['stats']['confirmed'] += 1
            elif pos.confirm_status == CONFIRM_EXCLUDED:
                group['stats']['excluded'] += 1
            else:
                group['stats']['pending'] += 1

        return SuccessResponse(
            data={
                'company_groups': list(company_groups.values()),
                'booking_status': booking_order.booking_status,
            }
        )

    # ==================== 上刊订单创建辅助方法 ====================

    def _create_on_air_order(self, booking_order, request):
        """创建上刊订单（从 final_review_approve 调用）"""
        from datetime import datetime
        import random

        try:
            from dvadmin_twodev.airing_manage.on_air_order.models import OnAirOrderModel
            from dvadmin_twodev.airing_manage.on_air_order_detail.models import OnAirOrderDetailModel
            from dvadmin_twodev.airing_manage.on_air_order.serializers import OnAirOrderModelCreateSerializer
            from dvadmin_twodev.airing_manage.on_air_order_detail.serializers import OnAirOrderDetailModelCreateSerializer
        except ImportError:
            return {'success': False, 'message': '上刊订单模块未安装'}

        # 检查是否已有上刊订单
        existing = OnAirOrderModel.objects.filter(booking_order_id=booking_order.id, delete_mark=0).first()
        if existing:
            return {'success': True, 'order_no': existing.order_no, 'message': '上刊订单已存在'}

        # 生成订单号
        date_str = datetime.now().strftime('%Y%m%d')
        while True:
            random_str = str(random.randint(1000, 9999))
            order_no = f"ON-{date_str}-{random_str}"
            if not OnAirOrderModel.objects.filter(order_no=order_no).exists():
                break

        # 获取日期范围
        details = BookingOrderDetailModel.objects.filter(
            booking_order_id=booking_order.id, delete_mark=0, enabled_mark=1
        )
        start_dates = [d.start_date for d in details if d.start_date]
        end_dates = [d.end_date for d in details if d.end_date]

        if not start_dates or not end_dates:
            return {'success': False, 'message': '明细缺少日期信息'}

        # 创建上刊订单
        on_air_order_data = {
            'order_no': order_no,
            'booking_order_id': booking_order.id,
            'customer_name': booking_order.customer_name or '',
            'booking_start_date': min(start_dates),
            'booking_end_date': max(end_dates),
            'order_status': 4,
            'approved_time': timezone.now(),
            'remark': booking_order.remark or '',
        }

        serializer = OnAirOrderModelCreateSerializer(data=on_air_order_data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        on_air_order = serializer.save()

        # 获取已确认的车位（排除被剔除的）
        positions = VehicleAdPositionModel.objects.filter(
            booking_detail_id__booking_order_id=booking_order.id,
            delete_mark=0, enabled_mark=1,
            allocation_status=1,
            confirm_status__in=[CONFIRM_CONFIRMED, CONFIRM_PENDING],  # 已确认或待确认都包含
        ).select_related('resource_id__base_media_type_id', 'booking_detail_id__media_type_id', 'vehicle_id')

        created_count = 0
        for position in positions:
            try:
                base_media_type = position.resource_id.base_media_type_id if position.resource_id else None
                booking_detail = position.booking_detail_id
                composite_media_type = None
                composite_media_type_name = None

                if booking_detail and booking_detail.is_composite and booking_detail.media_type_id:
                    composite_media_type = booking_detail.media_type_id
                    composite_media_type_name = booking_detail.media_type_name or ''

                detail_data = {
                    'order_id': on_air_order.id,
                    'position_id': position.id,
                    'roadline_id': position.roadline_id_id,
                    'roadline_name': position.roadline_name or '',
                    'roadline_company_id': position.roadline_company_id_id,
                    'roadline_company_name': position.roadline_company_name or '',
                    'plan_vehicle_id': position.vehicle_id_id,
                    'plan_vehicle_no': position.vehicle_no or '',
                    'composite_media_type_id': composite_media_type.id if composite_media_type else None,
                    'composite_media_type_name': composite_media_type_name or '',
                    'base_media_type_id': base_media_type.id if base_media_type else None,
                    'base_media_type_name': base_media_type.media_name if base_media_type else '',
                    'execution_status': 1,
                }

                detail_serializer = OnAirOrderDetailModelCreateSerializer(
                    data=detail_data, context={'request': request}
                )
                detail_serializer.is_valid(raise_exception=True)
                detail_serializer.save()
                created_count += 1
            except Exception as e:
                print(f"[创建上刊明细] 失败: position_id={position.id}, error={str(e)}")
                continue

        return {
            'success': True,
            'order_no': on_air_order.order_no,
            'created_detail_count': created_count,
            'message': f"上刊订单 {order_no} 已创建，共 {created_count} 条明细"
        }

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
        兼容旧接口：直接审核通过预订单
        对于新流程的订单会根据当前状态路由到对应的审批操作

        POST /api/BookingOrderModelViewSet/{id}/approve/
        """
        booking_order = self.get_object()

        # 根据当前状态路由
        if booking_order.booking_status == STATUS_MEDIA_FIRST:
            return self.first_review_approve(request, pk)
        elif booking_order.booking_status == STATUS_MEDIA_FINAL:
            return self.final_review_approve(request, pk)
        elif booking_order.booking_status == STATUS_APPROVED:
            return ErrorResponse(msg="该订单已审核通过", code=400)
        elif booking_order.booking_status == STATUS_REJECTED:
            return ErrorResponse(msg="该订单已被驳回", code=400)
        else:
            # 兼容旧流程：直接通过
            review_comment = request.data.get('review_comment', '')
            booking_order.booking_status = STATUS_APPROVED
            booking_order.current_approval_node = None
            booking_order.approved_time = timezone.now()
            if review_comment:
                booking_order.remark = (booking_order.remark or '') + f"\n[审核意见] {review_comment}"
            booking_order.save()

            on_air_result = self._create_on_air_order(booking_order, request)
            msg = "审核通过"
            if on_air_result.get('success'):
                msg += f"，已创建上刊订单（{on_air_result.get('order_no', '')}）"

            return SuccessResponse(
                data={'id': str(booking_order.id), 'on_air_result': on_air_result},
                msg=msg
            )

