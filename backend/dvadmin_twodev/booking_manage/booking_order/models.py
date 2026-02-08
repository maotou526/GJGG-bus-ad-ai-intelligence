'''
Description: 预订订单模型
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.db import models
from django.conf import settings
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.booking_manage.customer.models import CustomerModel
from conf.env import CUS_TABLE_PREFIX


class BookingOrderModel(BaseDataModel):
    """
    预订订单模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 预订单号
    booking_no = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        verbose_name="预订单号",
        help_text="唯一编号，自动生成，格式：BK-YYYYMMDD-XXXX",
        db_comment="预订单号，唯一编号，自动生成，格式：BK-YYYYMMDD-XXXX"
    )

    # 客户ID
    customer_id = models.ForeignKey(
        CustomerModel,
        on_delete=models.PROTECT,
        db_column='customer_id',
        db_constraint=False,
        null=False,
        blank=False,
        verbose_name="客户ID",
        help_text="关联客户表",
        db_comment="客户ID，关联客户表"
    )

    # 客户名称（冗余字段）
    customer_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="客户名称",
        help_text="冗余字段，便于查询",
        db_comment="客户名称，冗余字段，便于查询"
    )

    # 预订单类型
    booking_type = models.IntegerField(
        null=False,
        blank=False,
        verbose_name="预订单类型",
        help_text="预订单类型：1=新预订, 2=续期, 3=变更",
        db_comment="预订单类型：1=新预订, 2=续期, 3=变更"
    )

    # 原预订单ID
    original_booking_id = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        db_column='original_booking_id',
        db_constraint=False,
        null=True,
        blank=True,
        related_name='related_orders',
        verbose_name="原预订单ID",
        help_text="如果是变更/续期，关联原预订单",
        db_comment="原预订单ID，如果是变更/续期，关联原预订单"
    )

    # 预订单状态
    booking_status = models.IntegerField(
        null=False,
        blank=False,
        default=3,
        verbose_name="预订单状态",
        help_text="预订单状态：1=草稿, 2=待审批, 3=审批中, 4=已通过, 5=已完成, 6=已取消, 7=已驳回",
        db_comment="预订单状态：1=草稿, 2=待审批, 3=审批中, 4=已通过, 5=已完成, 6=已取消, 7=已驳回"
    )

    # 广告内容描述
    ad_content = models.TextField(
        null=True,
        blank=True,
        verbose_name="广告内容描述",
        help_text="广告内容简述",
        db_comment="广告内容描述，广告内容简述"
    )

    # 投放开始日期（已废弃，由明细表管理）
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="投放开始日期",
        help_text="计划投放开始日期（已废弃，由明细表管理）",
        db_comment="投放开始日期，计划投放开始日期（已废弃，由明细表管理）"
    )

    # 投放结束日期（已废弃，由明细表管理）
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="投放结束日期",
        help_text="计划投放结束日期（已废弃，由明细表管理）",
        db_comment="投放结束日期，计划投放结束日期（已废弃，由明细表管理）"
    )

    # 投放天数
    duration_days = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="投放天数",
        help_text="自动计算的投放天数",
        db_comment="投放天数，自动计算的投放天数"
    )

    # 订单金额
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="订单金额",
        help_text="订单总金额（元）",
        db_comment="订单金额，订单总金额（元）"
    )

    # 已支付金额
    paid_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        default=0,
        verbose_name="已支付金额",
        help_text="已支付金额（元）",
        db_comment="已支付金额，已支付金额（元）"
    )

    # 审批完成时间
    approved_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="审批完成时间",
        help_text="审批通过时间",
        db_comment="审批完成时间，审批通过时间"
    )

    # 提交人ID
    submitter_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        db_column='submitter_id',
        db_constraint=False,
        null=True,
        blank=True,
        related_name='submitted_booking_orders',
        verbose_name="提交人ID",
        help_text="订单提交人",
        db_comment="提交人ID，订单提交人"
    )

    # 提交时间
    submit_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="提交时间",
        help_text="订单提交时间",
        db_comment="提交时间，订单提交时间"
    )

    # 备注
    remark = models.TextField(
        null=True,
        blank=True,
        verbose_name="备注",
        help_text="其他说明",
        db_comment="备注，其他说明"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "booking_order"
        verbose_name = "预订订单表"
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
        indexes = [
            models.Index(fields=['booking_no']),
            models.Index(fields=['customer_id']),
            models.Index(fields=['booking_type']),
            models.Index(fields=['booking_status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['original_booking_id']),
        ]

