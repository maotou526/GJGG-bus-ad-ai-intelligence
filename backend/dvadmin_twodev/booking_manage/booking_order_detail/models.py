'''
Description: 预订订单明细模型
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.booking_manage.booking_order.models import BookingOrderModel
from dvadmin_twodev.basedata.roadline.models import RoadlineModel
from dvadmin_twodev.basedata.company.models import CompanyModel
from dvadmin_twodev.basedata.media_type.models import AdMediaTypeModel
from conf.env import CUS_TABLE_PREFIX


class BookingOrderDetailModel(BaseDataModel):
    """
    预订订单明细模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 预订单ID
    booking_order_id = models.ForeignKey(
        BookingOrderModel,
        on_delete=models.CASCADE,
        db_column='booking_order_id',
        db_constraint=False,
        null=False,
        blank=False,
        related_name='details',
        verbose_name="预订单ID",
        help_text="关联预订订单表",
        db_comment="预订单ID，关联预订订单表"
    )

    # 线路ID
    roadline_id = models.ForeignKey(
        RoadlineModel,
        on_delete=models.PROTECT,
        db_column='roadline_id',
        db_constraint=False,
        null=False,
        blank=False,
        verbose_name="线路ID",
        help_text="关联线路表",
        db_comment="线路ID，关联线路表"
    )

    # 线路名称（冗余字段）
    roadline_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="线路名称",
        help_text="冗余字段",
        db_comment="线路名称，冗余字段"
    )

    # 营运公司ID
    roadline_company_id = models.ForeignKey(
        CompanyModel,
        on_delete=models.PROTECT,
        db_column='roadline_company_id',
        db_constraint=False,
        null=False,
        blank=False,
        verbose_name="营运公司ID",
        help_text="线路所属营运公司",
        db_comment="营运公司ID，线路所属营运公司"
    )

    # 营运公司名称（冗余字段）
    roadline_company_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="营运公司名称",
        help_text="冗余字段",
        db_comment="营运公司名称，冗余字段"
    )

    # 媒体类型ID
    media_type_id = models.ForeignKey(
        AdMediaTypeModel,
        on_delete=models.PROTECT,
        db_column='media_type_id',
        db_constraint=False,
        null=False,
        blank=False,
        verbose_name="媒体类型ID",
        help_text="关联媒体类型表，组合或基础类型",
        db_comment="媒体类型ID，关联媒体类型表，组合或基础类型"
    )

    # 媒体类型名称（冗余字段）
    media_type_name = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="媒体类型名称",
        help_text="冗余字段",
        db_comment="媒体类型名称，冗余字段"
    )

    # 是否组合类型
    is_composite = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="是否组合类型",
        help_text="True=组合类型(如大三侧)，False=基础类型",
        db_comment="是否组合类型，True=组合类型(如大三侧)，False=基础类型"
    )

    # 预订数量
    quantity = models.IntegerField(
        null=False,
        blank=False,
        verbose_name="预订数量",
        help_text="预订的车辆数量",
        db_comment="预订数量，预订的车辆数量"
    )

    # 单价
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="单价",
        help_text="单价（元/月或元/年）",
        db_comment="单价，单价（元/月或元/年）"
    )

    # 小计金额
    subtotal_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="小计金额",
        help_text="明细小计金额",
        db_comment="小计金额，明细小计金额"
    )

    # 资源锁定状态
    lock_status = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        verbose_name="资源锁定状态",
        help_text="资源锁定状态：1=未锁定, 2=已锁定, 3=已释放",
        db_comment="资源锁定状态：1=未锁定, 2=已锁定, 3=已释放"
    )

    # 投放开始日期
    start_date = models.DateField(
        null=False,
        blank=False,
        verbose_name="投放开始日期",
        help_text="计划投放开始日期",
        db_comment="投放开始日期，计划投放开始日期"
    )

    # 投放结束日期
    end_date = models.DateField(
        null=False,
        blank=False,
        verbose_name="投放结束日期",
        help_text="计划投放结束日期",
        db_comment="投放结束日期，计划投放结束日期"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "booking_order_detail"
        verbose_name = "预订订单明细表"
        verbose_name_plural = verbose_name
        ordering = ['booking_order_id', 'roadline_id', 'media_type_id']
        indexes = [
            models.Index(fields=['booking_order_id']),
            models.Index(fields=['roadline_id']),
            models.Index(fields=['roadline_company_id']),
            models.Index(fields=['media_type_id']),
            models.Index(fields=['lock_status']),
        ]
