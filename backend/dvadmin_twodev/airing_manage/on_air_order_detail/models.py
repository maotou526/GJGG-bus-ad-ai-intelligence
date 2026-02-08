'''
Description: 上刊订单明细模型
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.airing_manage.on_air_order.models import OnAirOrderModel
from dvadmin_twodev.booking_manage.vehicle_ad_position.models import VehicleAdPositionModel
from dvadmin_twodev.basedata.roadline.models import RoadlineModel
from dvadmin_twodev.basedata.company.models import CompanyModel
from dvadmin_twodev.basedata.vehicle.models import VehicleModel
from dvadmin_twodev.basedata.media_type.models import AdMediaTypeModel
from conf.env import CUS_TABLE_PREFIX


class OnAirOrderDetailModel(BaseDataModel):
    """
    上刊订单明细模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 上刊订单ID
    order_id = models.ForeignKey(
        OnAirOrderModel,
        on_delete=models.PROTECT,
        db_column="order_id",
        db_constraint=False,
        null=False,
        blank=False,
        verbose_name="上刊订单ID",
        help_text="关联上刊订单表（dwd_on_air_order）",
        db_comment="上刊订单ID，关联上刊订单表（dwd_on_air_order）",
        related_name="on_air_order_details",
    )

    # 车位广告ID
    position_id = models.ForeignKey(
        VehicleAdPositionModel,
        on_delete=models.PROTECT,
        db_column="position_id",
        db_constraint=False,
        null=False,
        blank=False,
        verbose_name="车位广告ID",
        help_text="关联车位广告表（预订的车位广告）",
        db_comment="车位广告ID，关联车位广告表（预订的车位广告）",
        related_name="on_air_order_details",
    )

    # 线路ID（冗余字段）
    roadline_id = models.ForeignKey(
        RoadlineModel,
        on_delete=models.PROTECT,
        db_column="roadline_id",
        db_constraint=False,
        null=False,
        blank=False,
        verbose_name="线路ID",
        help_text="冗余字段便于查询",
        db_comment="线路ID，冗余字段便于查询",
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
        db_column="roadline_company_id",
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

    # 预订车辆ID
    plan_vehicle_id = models.ForeignKey(
        VehicleModel,
        on_delete=models.SET_NULL,
        db_column="plan_vehicle_id",
        db_constraint=False,
        null=True,
        blank=True,
        related_name="plan_on_air_order_details",
        verbose_name="预订车辆ID",
        help_text="预订的车辆ID",
        db_comment="预订车辆ID，预订的车辆ID"
    )

    # 预订车辆自编号
    plan_vehicle_no = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="预订车辆自编号",
        help_text="预订的车辆自编号",
        db_comment="预订车辆自编号，预订的车辆自编号"
    )

    # 实际上刊车辆ID
    act_vehicle_id = models.ForeignKey(
        VehicleModel,
        on_delete=models.SET_NULL,
        db_column="act_vehicle_id",
        db_constraint=False,
        null=True,
        blank=True,
        related_name="act_on_air_order_details",
        verbose_name="实际上刊车辆ID",
        help_text="实际上刊的车辆ID（可能与预订不同）",
        db_comment="实际上刊车辆ID，实际上刊的车辆ID（可能与预订不同）"
    )

    # 实际上刊车辆自编号
    act_vehicle_no = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="实际上刊车辆自编号",
        help_text="实际上刊的车辆自编号",
        db_comment="实际上刊车辆自编号，实际上刊的车辆自编号"
    )

    # 组合媒体类型ID
    composite_media_type_id = models.ForeignKey(
        AdMediaTypeModel,
        on_delete=models.SET_NULL,
        db_column="composite_media_type_id",
        db_constraint=False,
        null=True,
        blank=True,
        related_name="composite_on_air_order_details",
        verbose_name="组合媒体类型ID",
        help_text="预订时的组合类型ID（如'大三侧'），NULL表示单独预订基础类型",
        db_comment="组合媒体类型ID，预订时的组合类型ID（如'大三侧'），NULL表示单独预订基础类型"
    )

    # 组合媒体类型名称（冗余字段）
    composite_media_type_name = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="组合媒体类型名称",
        help_text="冗余字段，如'大三侧'、'全车身'",
        db_comment="组合媒体类型名称，冗余字段，如'大三侧'、'全车身'"
    )

    # 基础媒体类型ID
    base_media_type_id = models.ForeignKey(
        AdMediaTypeModel,
        on_delete=models.PROTECT,
        db_column="base_media_type_id",
        db_constraint=False,
        null=False,
        blank=False,
        related_name="base_on_air_order_details",
        verbose_name="基础媒体类型ID",
        help_text="关联媒体类型表（基础类型）",
        db_comment="基础媒体类型ID，关联媒体类型表（基础类型）"
    )

    # 基础媒体类型名称（冗余字段）
    base_media_type_name = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="基础媒体类型名称",
        help_text="冗余字段，如'车头'、'车尾'、'左侧'、'右侧'",
        db_comment="基础媒体类型名称，冗余字段，如'车头'、'车尾'、'左侧'、'右侧'"
    )

    # 实际上刊时间
    act_on_air_datetime = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="实际上刊时间",
        help_text="实际上刊时间（精确到时分秒）",
        db_comment="实际上刊时间，实际上刊时间（精确到时分秒）"
    )

    # 执行状态
    execution_status = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        verbose_name="执行状态",
        help_text="执行状态：1=待执行, 2=施工中, 3=已完成",
        db_comment="执行状态：1=待执行, 2=施工中, 3=已完成"
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
        db_table = CUS_TABLE_PREFIX + "on_air_order_detail"
        verbose_name = "上刊订单明细表"
        verbose_name_plural = verbose_name
        ordering = ["-create_datetime"]
        indexes = [
            models.Index(fields=["order_id"]),
            models.Index(fields=["position_id"]),
            models.Index(fields=["roadline_id"]),
            models.Index(fields=["roadline_company_id"]),
            models.Index(fields=["plan_vehicle_id"]),
            models.Index(fields=["act_vehicle_id"]),
            models.Index(fields=["base_media_type_id"]),
            models.Index(fields=["execution_status"]),
            models.Index(fields=["act_on_air_datetime"]),
        ]
