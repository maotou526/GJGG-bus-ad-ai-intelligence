'''
Description: 车位广告模型
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.db import models

from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.booking_manage.booking_order_detail.models import BookingOrderDetailModel
from dvadmin_twodev.basedata.roadline.models import RoadlineModel
from dvadmin_twodev.basedata.company.models import CompanyModel
from dvadmin_twodev.basedata.vehicle_ad_resource.models import VehicleAdResourceModel
from dvadmin_twodev.basedata.vehicle.models import VehicleModel
from conf.env import CUS_TABLE_PREFIX


class VehicleAdPositionModel(BaseDataModel):
    """
    车位广告模型（dwd_vehicle_ad_position）
    继承自BaseDataModel, 自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 预订单明细ID（车身广告）
    booking_detail_id = models.ForeignKey(
        BookingOrderDetailModel,
        on_delete=models.CASCADE,
        db_column="booking_detail_id",
        db_constraint=False,
        null=False,
        blank=False,
        related_name="vehicle_ad_positions",
        verbose_name="预订单明细ID",
        help_text="关联预订单明细表（车身广告）",
        db_comment="预订单明细ID，关联预订单明细表（车身广告）",
    )

    # 线路ID（冗余，便于查询）
    roadline_id = models.ForeignKey(
        RoadlineModel,
        on_delete=models.PROTECT,
        db_column="roadline_id",
        db_constraint=False,
        null=False,
        blank=False,
        verbose_name="线路ID",
        help_text="关联线路表，冗余字段便于查询",
        db_comment="线路ID，关联线路表，冗余字段便于查询",
    )

    # 线路名称（冗余字段）
    roadline_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="线路名称",
        help_text="线路名称，冗余字段",
        db_comment="线路名称，冗余字段",
    )

    # 营运公司ID（线路所属营运公司）
    roadline_company_id = models.ForeignKey(
        CompanyModel,
        on_delete=models.PROTECT,
        db_column="roadline_company_id",
        db_constraint=False,
        null=False,
        blank=False,
        verbose_name="营运公司ID",
        help_text="线路所属营运公司，关联公司表",
        db_comment="营运公司ID，线路所属营运公司，关联公司表",
    )

    # 营运公司名称（冗余字段）
    roadline_company_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="营运公司名称",
        help_text="营运公司名称，冗余字段",
        db_comment="营运公司名称，冗余字段",
    )

    # 车辆资源位ID
    resource_id = models.ForeignKey(
        VehicleAdResourceModel,
        on_delete=models.PROTECT,
        db_column="resource_id",
        db_constraint=False,
        null=False,
        blank=False,
        verbose_name="车辆资源位ID",
        help_text="关联车辆广告资源位表（dwd_vehicle_ad_resource）",
        db_comment="车辆资源位ID，关联车辆广告资源位表（dwd_vehicle_ad_resource）",
    )

    # 车辆ID（冗余，便于查询）
    vehicle_id = models.ForeignKey(
        VehicleModel,
        on_delete=models.PROTECT,
        db_column="vehicle_id",
        db_constraint=False,
        null=False,
        blank=False,
        verbose_name="车辆ID",
        help_text="关联车辆表，冗余字段便于查询",
        db_comment="车辆ID，关联车辆表，冗余字段便于查询",
    )

    # 车辆自编号（冗余字段）
    vehicle_no = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="车辆自编号",
        help_text="车辆自编号，冗余字段",
        db_comment="车辆自编号，冗余字段",
    )

    # 预订开始日期
    reserved_start_date = models.DateField(
        null=False,
        blank=False,
        verbose_name="预订开始日期",
        help_text="该资源位的预订起始日期",
        db_comment="预订开始日期，该资源位的预订起始日期",
    )

    # 预订结束日期
    reserved_end_date = models.DateField(
        null=False,
        blank=False,
        verbose_name="预订结束日期",
        help_text="该资源位的预订结束日期",
        db_comment="预订结束日期，该资源位的预订结束日期",
    )

    # 实际上刊日期（工单完成后回填）
    actual_on_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="实际上刊日期",
        help_text="实际上刊日期（工单完成后回填）",
        db_comment="实际上刊日期，工单完成后回填",
    )

    # 实际下刊日期（工单完成后回填）
    actual_off_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="实际下刊日期",
        help_text="实际下刊日期（工单完成后回填）",
        db_comment="实际下刊日期，工单完成后回填",
    )

    # 分配状态：1=已分配, 2=已上刊, 3=已下刊, 4=已取消
    allocation_status = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        verbose_name="分配状态",
        help_text="分配状态：1=已分配, 2=已上刊, 3=已下刊, 4=已取消",
        db_comment="分配状态：1=已分配, 2=已上刊, 3=已下刊, 4=已取消",
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "vehicle_ad_position"
        verbose_name = "车位广告表"
        verbose_name_plural = verbose_name
        ordering = ["booking_detail_id", "roadline_id", "vehicle_id"]
        indexes = [
            models.Index(fields=["booking_detail_id"]),
            models.Index(fields=["roadline_id"]),
            models.Index(fields=["roadline_company_id"]),
            models.Index(fields=["resource_id"]),
            models.Index(fields=["vehicle_id"]),
            models.Index(fields=["allocation_status"]),
            models.Index(fields=["reserved_start_date", "reserved_end_date"]),
        ]
