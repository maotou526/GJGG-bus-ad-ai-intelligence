'''
Description: 车位广告变更历史模型
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.conf import settings
from django.db import models

from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.booking_manage.booking_order.models import BookingOrderModel
from dvadmin_twodev.booking_manage.booking_order_detail.models import BookingOrderDetailModel
from dvadmin_twodev.booking_manage.vehicle_ad_position.models import VehicleAdPositionModel
from dvadmin_twodev.basedata.roadline.models import RoadlineModel
from dvadmin_twodev.basedata.company.models import CompanyModel
from dvadmin_twodev.basedata.vehicle.models import VehicleModel
from dvadmin_twodev.basedata.vehicle_ad_resource.models import VehicleAdResourceModel
from conf.env import CUS_TABLE_PREFIX


class VehicleAdPositionChangeModel(BaseDataModel):
    """
    车位广告变更历史模型（dwd_vehicle_ad_position_change）

    用于记录审批过程中对车位广告的调整历史（新增、删除、修改），
    便于完整追溯审批过程中的车辆分配变化。
    """

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
    )

    # 预订单明细ID（可选）
    booking_detail_id = models.ForeignKey(
        BookingOrderDetailModel,
        on_delete=models.SET_NULL,
        db_column="booking_detail_id",
        db_constraint=False,
        null=True,
        blank=True,
        verbose_name="预订单明细ID",
        help_text="关联预订单明细表（可选）",
        db_comment="预订单明细ID，关联预订单明细表（可选）",
    )

    # 操作类型：1=新增车位, 2=删除车位, 3=修改车位
    action_type = models.IntegerField(
        null=False,
        blank=False,
        verbose_name="操作类型",
        help_text="操作类型：1=新增车位, 2=删除车位, 3=修改车位",
        db_comment="操作类型：1=新增车位, 2=删除车位, 3=修改车位",
    )

    # 车位广告ID（新增时为NULL）
    position_id = models.ForeignKey(
        VehicleAdPositionModel,
        on_delete=models.SET_NULL,
        db_column="position_id",
        db_constraint=False,
        null=True,
        blank=True,
        verbose_name="车位广告ID",
        help_text="关联车位广告表（新增时为NULL）",
        db_comment="车位广告ID，关联车位广告表（新增时为NULL）",
    )

    # 线路ID（可选）
    roadline_id = models.ForeignKey(
        RoadlineModel,
        on_delete=models.SET_NULL,
        db_column="roadline_id",
        db_constraint=False,
        null=True,
        blank=True,
        verbose_name="线路ID",
        help_text="关联线路表（可选）",
        db_comment="线路ID，关联线路表（可选）",
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

    # 营运公司ID（可选）
    roadline_company_id = models.ForeignKey(
        CompanyModel,
        on_delete=models.SET_NULL,
        db_column="roadline_company_id",
        db_constraint=False,
        null=True,
        blank=True,
        verbose_name="营运公司ID",
        help_text="线路所属营运公司（可选）",
        db_comment="营运公司ID，线路所属营运公司（可选）",
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

    # 车辆ID（可选）
    vehicle_id = models.ForeignKey(
        VehicleModel,
        on_delete=models.SET_NULL,
        db_column="vehicle_id",
        db_constraint=False,
        null=True,
        blank=True,
        verbose_name="车辆ID",
        help_text="关联车辆表（可选）",
        db_comment="车辆ID，关联车辆表（可选）",
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

    # 资源位ID（可选）
    resource_id = models.ForeignKey(
        VehicleAdResourceModel,
        on_delete=models.SET_NULL,
        db_column="resource_id",
        db_constraint=False,
        null=True,
        blank=True,
        verbose_name="资源位ID",
        help_text="关联车辆广告资源位表（可选）",
        db_comment="资源位ID，关联车辆广告资源位表（可选）",
    )

    # 变更前数据（JSON）
    before_data = models.CharField(
        null=True,
        blank=True,
        verbose_name="变更前数据",
        help_text="修改/删除时，记录变更前的完整数据",
        db_comment="变更前数据，修改/删除时记录变更前的完整数据",
    )

    # 变更后数据（JSON）
    after_data = models.CharField(
        null=True,
        blank=True,
        verbose_name="变更后数据",
        help_text="修改/新增时，记录变更后的完整数据",
        db_comment="变更后数据，修改/新增时记录变更后的完整数据",
    )

    # 变更原因
    change_reason = models.TextField(
        null=True,
        blank=True,
        verbose_name="变更原因",
        help_text="调整原因说明",
        db_comment="变更原因，调整原因说明",
    )

    # 变更节点：1=媒体部初审, 2=营运公司审核, 3=媒体部复审
    change_node = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="变更节点",
        help_text="变更节点：1=媒体部初审, 2=营运公司审核, 3=媒体部复审",
        db_comment="变更节点：1=媒体部初审, 2=营运公司审核, 3=媒体部复审",
    )

    # 操作人ID
    operator_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        db_column="operator_id",
        db_constraint=False,
        null=True,
        blank=True,
        verbose_name="操作人ID",
        help_text="操作人",
        db_comment="操作人ID，操作人",
    )

    # 操作时间
    operation_time = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name="操作时间",
        help_text="操作时间",
        db_comment="操作时间",
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "vehicle_ad_position_change"
        verbose_name = "车位广告变更历史表"
        verbose_name_plural = verbose_name
        ordering = ["-operation_time"]
        indexes = [
            models.Index(fields=["booking_order_id"]),
            models.Index(fields=["booking_detail_id"]),
            models.Index(fields=["position_id"]),
            models.Index(fields=["roadline_id"]),
            models.Index(fields=["roadline_company_id"]),
            models.Index(fields=["vehicle_id"]),
            models.Index(fields=["resource_id"]),
            models.Index(fields=["action_type"]),
            models.Index(fields=["change_node"]),
            models.Index(fields=["operation_time"]),
        ]

