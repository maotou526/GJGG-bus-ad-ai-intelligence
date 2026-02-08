'''
Description: 上刊订单模型
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.booking_manage.booking_order.models import BookingOrderModel
from conf.env import CUS_TABLE_PREFIX


class OnAirOrderModel(BaseDataModel):
    """
    上刊订单模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 订单号
    order_no = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        unique=True,
        verbose_name="订单号",
        help_text="唯一编号，格式：ON-YYYYMMDD-XXXX",
        db_comment="订单号，唯一编号，格式：ON-YYYYMMDD-XXXX"
    )

    # 预订单ID
    booking_order_id = models.ForeignKey(
        BookingOrderModel,
        on_delete=models.PROTECT,
        db_column="booking_order_id",
        db_constraint=False,
        null=False,
        blank=False,
        verbose_name="预订单ID",
        help_text="关联预订单表（dwd_booking_order）",
        db_comment="预订单ID，关联预订单表（dwd_booking_order）",
        related_name="on_air_orders",
    )

    # 客户名称（冗余字段）
    customer_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="客户名称",
        help_text="客户名称，冗余字段",
        db_comment="客户名称，冗余字段"
    )

    # 投放开始日期
    booking_start_date = models.DateField(
        null=False,
        blank=False,
        verbose_name="投放开始日期",
        help_text="投放开始日期（来自预订单start_date）",
        db_comment="投放开始日期，来自预订单start_date"
    )

    # 投放结束日期
    booking_end_date = models.DateField(
        null=False,
        blank=False,
        verbose_name="投放结束日期",
        help_text="投放结束日期（来自预订单end_date）",
        db_comment="投放结束日期，来自预订单end_date"
    )

    # 订单状态
    order_status = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        verbose_name="订单状态",
        help_text="订单状态：1=草稿, 2=待审批, 3=审批中, 4=已通过, 5=施工中, 6=已完成, 7=已驳回",
        db_comment="订单状态：1=草稿, 2=待审批, 3=审批中, 4=已通过, 5=施工中, 6=已完成, 7=已驳回"
    )

    # 审批完成时间
    approved_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="审批完成时间",
        help_text="审批通过时间",
        db_comment="审批完成时间，审批通过时间"
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
        db_table = CUS_TABLE_PREFIX + "on_air_order"
        verbose_name = "上刊订单表"
        verbose_name_plural = verbose_name
        ordering = ["-create_datetime"]
        indexes = [
            models.Index(fields=["booking_order_id"]),
            models.Index(fields=["order_status"]),
            models.Index(fields=["booking_start_date", "booking_end_date"]),
            models.Index(fields=["order_no"]),
        ]
