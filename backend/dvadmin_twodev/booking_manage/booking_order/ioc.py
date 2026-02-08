"""
预订单模块 IOC 方法

提供预订单审批流程中的：
1. 审核人 IOC：动态获取各审批节点的审核人
2. 执行 IOC：流程流转时触发的业务逻辑（车位分配/释放、状态变更、上刊订单创建等）

IOC 方法通过 @register_workflow_method 装饰器自动注册，
被工作流引擎在节点/连线上配置后自动调用。
"""
import json
import logging
from typing import List, Dict, Any
from datetime import datetime

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from dvadmin_twodev.node_workflow.ioc import (
    IWorkflowMethod,
    WfMethodParameter,
    register_workflow_method,
)

logger = logging.getLogger(__name__)

# ============================================================
# 常量（与 views.py 保持一致）
# ============================================================
STATUS_DRAFT = 1
STATUS_MEDIA_FIRST = 2
STATUS_COMPANY_REVIEW = 3
STATUS_MEDIA_FINAL = 4
STATUS_APPROVED = 5
STATUS_COMPLETED = 6
STATUS_REJECTED = 7
STATUS_CANCELLED = 8

NODE_MEDIA_FIRST = 1
NODE_COMPANY_REVIEW = 2
NODE_MEDIA_FINAL = 3

CONFIRM_PENDING = 1
CONFIRM_CONFIRMED = 2
CONFIRM_EXCLUDED = 3


def _get_booking_order(params: WfMethodParameter):
    """从 IOC 参数中获取预订单对象"""
    from dvadmin_twodev.booking_manage.booking_order.models import BookingOrderModel
    booking_order_id = (params.form_data or {}).get('booking_order_id') or params.process_id
    if not booking_order_id:
        return None
    try:
        return BookingOrderModel.objects.get(id=booking_order_id, delete_mark=0)
    except BookingOrderModel.DoesNotExist:
        logger.error(f"[BookingIOC] 预订单不存在: {booking_order_id}")
        return None


# ============================================================
# 审核人 IOC 方法
# ============================================================

@register_workflow_method
class GetBookingMediaReviewers(IWorkflowMethod):
    """
    获取媒体部审核人（用于媒体部初审/复审节点）

    逻辑：
    - 查找角色为"媒体部审核员"的用户
    - 如果未配置角色，返回预订单提交人的上级部门负责人
    """

    @property
    def name(self) -> str:
        return "GetBookingMediaReviewers"

    @property
    def description(self) -> str:
        return "获取预订单媒体部审核人员列表"

    def get_user_ids(self, params: WfMethodParameter) -> List[str]:
        from django.contrib.auth import get_user_model
        from dvadmin.system.models import Role

        User = get_user_model()
        user_ids = []

        # 方案1：通过角色获取媒体部审核人
        try:
            media_roles = Role.objects.filter(
                Q(name__contains='媒体') | Q(key__contains='media_reviewer'),
                status=1
            )
            if media_roles.exists():
                for role in media_roles:
                    role_users = User.objects.filter(
                        role=role, is_active=True
                    ).values_list('id', flat=True)
                    user_ids.extend([str(uid) for uid in role_users])
        except Exception as e:
            logger.warning(f"[GetBookingMediaReviewers] 角色查询失败: {e}")

        # 方案2：如果角色未匹配到用户，取预订单创建者所在部门的负责人
        if not user_ids:
            booking_order = _get_booking_order(params)
            if booking_order and booking_order.creator:
                try:
                    creator = booking_order.creator
                    if hasattr(creator, 'dept') and creator.dept:
                        dept = creator.dept
                        # 获取部门负责人
                        dept_leaders = User.objects.filter(
                            dept=dept, is_active=True
                        ).exclude(id=creator.id).values_list('id', flat=True)
                        user_ids.extend([str(uid) for uid in dept_leaders[:3]])
                except Exception as e:
                    logger.warning(f"[GetBookingMediaReviewers] 部门负责人查询失败: {e}")

        logger.info(f"[GetBookingMediaReviewers] 返回审核人: {user_ids}")
        return list(set(user_ids))


@register_workflow_method
class GetBookingCompanyReviewers(IWorkflowMethod):
    """
    获取营运公司审核人（用于营运公司审核节点）

    逻辑：
    - 根据预订单明细中涉及的线路，获取对应营运公司的审核人
    - 每个营运公司返回至少一个审核人
    """

    @property
    def name(self) -> str:
        return "GetBookingCompanyReviewers"

    @property
    def description(self) -> str:
        return "根据预订单涉及的营运公司获取审核人员列表"

    def get_user_ids(self, params: WfMethodParameter) -> List[str]:
        from django.contrib.auth import get_user_model
        from dvadmin_twodev.booking_manage.booking_order_detail.models import BookingOrderDetailModel

        User = get_user_model()
        user_ids = []

        booking_order = _get_booking_order(params)
        if not booking_order:
            return []

        # 获取该预订单涉及的所有营运公司 ID
        company_ids = BookingOrderDetailModel.objects.filter(
            booking_order_id=booking_order.id,
            delete_mark=0, enabled_mark=1
        ).values_list('roadline_company_id', flat=True).distinct()

        # 根据营运公司查找对应审核人（用户所属部门对应的公司）
        for company_id in company_ids:
            if not company_id:
                continue
            try:
                company_users = User.objects.filter(
                    dept__company_id=company_id, is_active=True
                ).values_list('id', flat=True)
                user_ids.extend([str(uid) for uid in company_users[:5]])
            except Exception as e:
                logger.warning(f"[GetBookingCompanyReviewers] 查询公司 {company_id} 审核人失败: {e}")

        logger.info(f"[GetBookingCompanyReviewers] 返回审核人: {user_ids}")
        return list(set(user_ids))


# ============================================================
# 执行 IOC 方法（连线流转时触发的业务逻辑）
# ============================================================

@register_workflow_method
class BookingSubmitExecutor(IWorkflowMethod):
    """
    预订单提交执行器

    在流程从"开始节点"流转到"媒体部初审"节点时触发。
    业务逻辑：
    - 执行车位分配
    - 更新预订单状态为"待媒体部初审"
    """

    @property
    def name(self) -> str:
        return "BookingSubmitExecutor"

    @property
    def description(self) -> str:
        return "预订单提交 - 分配车位并进入初审"

    @transaction.atomic
    def execute(self, params: WfMethodParameter) -> bool:
        booking_order = _get_booking_order(params)
        if not booking_order:
            logger.error("[BookingSubmitExecutor] 预订单不存在")
            return False

        from dvadmin_twodev.booking_manage.booking_order.views import BookingOrderModelViewSet

        viewset = BookingOrderModelViewSet()

        # 执行车位分配
        result = viewset._allocate_positions_for_order(booking_order.id)
        if not result['success']:
            logger.error(f"[BookingSubmitExecutor] 车位分配失败: {result['message']}")
            return False

        # 更新状态
        booking_order.booking_status = STATUS_MEDIA_FIRST
        booking_order.current_approval_node = NODE_MEDIA_FIRST
        booking_order.submit_time = timezone.now()
        booking_order.reject_reason = None
        booking_order.reject_node = None
        booking_order.reject_user_id = None
        booking_order.reject_time = None
        booking_order.save()

        logger.info(f"[BookingSubmitExecutor] 预订单 {booking_order.booking_no} 提交成功")
        return True


@register_workflow_method
class BookingFirstReviewPassExecutor(IWorkflowMethod):
    """
    媒体部初审通过执行器

    在流程从"媒体部初审"流转到"营运公司审核"节点时触发。
    业务逻辑：
    - 重置所有车位的确认状态为"待确认"
    - 更新预订单状态为"待营运公司审核"
    """

    @property
    def name(self) -> str:
        return "BookingFirstReviewPassExecutor"

    @property
    def description(self) -> str:
        return "媒体部初审通过 - 重置车位确认状态，转营运公司"

    @transaction.atomic
    def execute(self, params: WfMethodParameter) -> bool:
        from dvadmin_twodev.booking_manage.vehicle_ad_position.models import VehicleAdPositionModel

        booking_order = _get_booking_order(params)
        if not booking_order:
            return False

        # 重置所有车位确认状态
        positions = VehicleAdPositionModel.objects.filter(
            booking_detail_id__booking_order_id=booking_order.id,
            delete_mark=0, enabled_mark=1, allocation_status=1
        )
        positions.update(
            confirm_status=CONFIRM_PENDING,
            confirm_user_id=None,
            confirm_time=None,
            exclude_reason=None
        )

        # 更新订单状态
        review_comment = (params.form_data or {}).get('review_comment', '')
        booking_order.booking_status = STATUS_COMPANY_REVIEW
        booking_order.current_approval_node = NODE_COMPANY_REVIEW
        if review_comment:
            booking_order.remark = (booking_order.remark or '') + f"\n[媒体部初审意见] {review_comment}"
        booking_order.save()

        logger.info(f"[BookingFirstReviewPassExecutor] 预订单 {booking_order.booking_no} 初审通过")
        return True


@register_workflow_method
class BookingFirstReviewRejectExecutor(IWorkflowMethod):
    """
    媒体部初审驳回执行器

    业务逻辑：
    - 释放已分配的车位
    - 更新预订单状态为"已驳回"
    """

    @property
    def name(self) -> str:
        return "BookingFirstReviewRejectExecutor"

    @property
    def description(self) -> str:
        return "媒体部初审驳回 - 释放车位"

    @transaction.atomic
    def execute(self, params: WfMethodParameter) -> bool:
        booking_order = _get_booking_order(params)
        if not booking_order:
            return False

        from dvadmin_twodev.booking_manage.booking_order.views import BookingOrderModelViewSet
        viewset = BookingOrderModelViewSet()
        viewset._release_positions_for_order(booking_order.id)

        reject_reason = (params.form_data or {}).get('reject_reason', '媒体部初审驳回')
        booking_order.booking_status = STATUS_REJECTED
        booking_order.current_approval_node = None
        booking_order.reject_reason = reject_reason
        booking_order.reject_node = NODE_MEDIA_FIRST
        booking_order.reject_time = timezone.now()
        booking_order.save()

        logger.info(f"[BookingFirstReviewRejectExecutor] 预订单 {booking_order.booking_no} 初审驳回")
        return True


@register_workflow_method
class BookingCompanyReviewCompleteExecutor(IWorkflowMethod):
    """
    营运公司审核完成执行器

    在流程从"营运公司审核"流转到"媒体部复审"节点时触发。
    业务逻辑：
    - 检查是否所有车位都已处理（确认/剔除）
    - 更新预订单状态为"待媒体部复审"
    """

    @property
    def name(self) -> str:
        return "BookingCompanyReviewCompleteExecutor"

    @property
    def description(self) -> str:
        return "营运公司审核完成 - 检查车位确认状态，转媒体部复审"

    @transaction.atomic
    def execute(self, params: WfMethodParameter) -> bool:
        from dvadmin_twodev.booking_manage.vehicle_ad_position.models import VehicleAdPositionModel

        booking_order = _get_booking_order(params)
        if not booking_order:
            return False

        # 检查是否还有待确认的车位
        pending_count = VehicleAdPositionModel.objects.filter(
            booking_detail_id__booking_order_id=booking_order.id,
            delete_mark=0, enabled_mark=1,
            allocation_status=1,
            confirm_status=CONFIRM_PENDING
        ).count()

        if pending_count > 0:
            logger.warning(
                f"[BookingCompanyReviewCompleteExecutor] 预订单 {booking_order.booking_no} "
                f"还有 {pending_count} 个车位未处理"
            )
            # 不阻断流程，但记录警告
            # 实际场景可以选择 return False 来阻断

        review_comment = (params.form_data or {}).get('review_comment', '')
        booking_order.booking_status = STATUS_MEDIA_FINAL
        booking_order.current_approval_node = NODE_MEDIA_FINAL
        if review_comment:
            booking_order.remark = (booking_order.remark or '') + f"\n[营运公司审核意见] {review_comment}"
        booking_order.save()

        logger.info(f"[BookingCompanyReviewCompleteExecutor] 预订单 {booking_order.booking_no} 营运审核完成")
        return True


@register_workflow_method
class BookingFinalReviewPassExecutor(IWorkflowMethod):
    """
    媒体部复审通过执行器

    在流程从"媒体部复审"流转到"结束"节点时触发。
    业务逻辑：
    - 更新预订单状态为"已通过"
    - 创建上刊订单
    """

    @property
    def name(self) -> str:
        return "BookingFinalReviewPassExecutor"

    @property
    def description(self) -> str:
        return "媒体部复审通过 - 创建上刊订单"

    @transaction.atomic
    def execute(self, params: WfMethodParameter) -> bool:
        booking_order = _get_booking_order(params)
        if not booking_order:
            return False

        review_comment = (params.form_data or {}).get('review_comment', '')

        booking_order.booking_status = STATUS_APPROVED
        booking_order.current_approval_node = None
        booking_order.approved_time = timezone.now()
        if review_comment:
            booking_order.remark = (booking_order.remark or '') + f"\n[媒体部复审意见] {review_comment}"
        booking_order.save()

        # 创建上刊订单
        from dvadmin_twodev.booking_manage.booking_order.views import BookingOrderModelViewSet
        viewset = BookingOrderModelViewSet()

        class _FakeRequest:
            """用于 _create_on_air_order 所需的 request 对象"""
            def __init__(self, user_id):
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    self.user = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    self.user = None

        fake_request = _FakeRequest(params.user_id)
        on_air_result = viewset._create_on_air_order(booking_order, fake_request)

        if on_air_result.get('success'):
            logger.info(
                f"[BookingFinalReviewPassExecutor] 预订单 {booking_order.booking_no} 复审通过，"
                f"上刊订单 {on_air_result.get('order_no')} 已创建"
            )
        else:
            logger.warning(
                f"[BookingFinalReviewPassExecutor] 上刊订单创建失败: {on_air_result.get('message')}"
            )

        return True


@register_workflow_method
class BookingFinalReviewRejectExecutor(IWorkflowMethod):
    """
    媒体部复审驳回执行器

    业务逻辑：
    - 释放已分配的车位
    - 更新预订单状态为"已驳回"
    """

    @property
    def name(self) -> str:
        return "BookingFinalReviewRejectExecutor"

    @property
    def description(self) -> str:
        return "媒体部复审驳回 - 释放车位"

    @transaction.atomic
    def execute(self, params: WfMethodParameter) -> bool:
        booking_order = _get_booking_order(params)
        if not booking_order:
            return False

        from dvadmin_twodev.booking_manage.booking_order.views import BookingOrderModelViewSet
        viewset = BookingOrderModelViewSet()
        viewset._release_positions_for_order(booking_order.id)

        reject_reason = (params.form_data or {}).get('reject_reason', '媒体部复审驳回')
        booking_order.booking_status = STATUS_REJECTED
        booking_order.current_approval_node = None
        booking_order.reject_reason = reject_reason
        booking_order.reject_node = NODE_MEDIA_FINAL
        booking_order.reject_time = timezone.now()
        booking_order.save()

        logger.info(f"[BookingFinalReviewRejectExecutor] 预订单 {booking_order.booking_no} 复审驳回")
        return True


@register_workflow_method
class BookingCancelExecutor(IWorkflowMethod):
    """
    预订单取消执行器

    业务逻辑：
    - 释放审批中的车位
    - 更新预订单状态为"已取消"
    """

    @property
    def name(self) -> str:
        return "BookingCancelExecutor"

    @property
    def description(self) -> str:
        return "预订单取消 - 释放车位并标记取消"

    @transaction.atomic
    def execute(self, params: WfMethodParameter) -> bool:
        booking_order = _get_booking_order(params)
        if not booking_order:
            return False

        if booking_order.booking_status in [STATUS_APPROVED, STATUS_COMPLETED, STATUS_CANCELLED]:
            logger.warning(f"[BookingCancelExecutor] 预订单状态不允许取消: {booking_order.booking_status}")
            return False

        # 审批中的订单需要释放车位
        if booking_order.booking_status in [STATUS_MEDIA_FIRST, STATUS_COMPANY_REVIEW, STATUS_MEDIA_FINAL]:
            from dvadmin_twodev.booking_manage.booking_order.views import BookingOrderModelViewSet
            viewset = BookingOrderModelViewSet()
            viewset._release_positions_for_order(booking_order.id)

        cancel_reason = (params.form_data or {}).get('cancel_reason', '')
        booking_order.booking_status = STATUS_CANCELLED
        booking_order.current_approval_node = None
        if cancel_reason:
            booking_order.remark = (booking_order.remark or '') + f"\n[取消原因] {cancel_reason}"
        booking_order.save()

        logger.info(f"[BookingCancelExecutor] 预订单 {booking_order.booking_no} 已取消")
        return True
