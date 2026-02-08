'''
Description: 车辆模型
Version: 1.0
Autor: 王晨
Date: 2025-10-18
LastEditors: 王晨
LastEditTime: 2025-10-18
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from conf.env import CUS_TABLE_PREFIX
from dvadmin_twodev.basedata.roadline.models import RoadlineModel


class VehicleModel(BaseDataModel):
    """
    车辆模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 公司名称
    company_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="公司名称",
        help_text="公司名称"
    )

    # 车队
    branch = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="车队",
        help_text="车队",
        db_comment="车队"
    )

    # 停车场名称
    park_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="停车场名称",
        help_text="停车场名称",
        db_comment="停车场名称"
    )

    # 所属线路（外键关联到dwd_roadline表）
    roadline = models.ForeignKey(
        RoadlineModel,
        on_delete=models.SET_NULL,
        db_column='roadline',  # 指定数据库列名为roadline，而不是默认的roadline_id
        db_constraint=False,  # 不创建数据库外键约束
        null=True,
        blank=True,
        verbose_name="所属线路",
        help_text="所属线路，关联到线路表",
        related_name="vehicles",
        db_comment="所属线路ID"
    )

    # 是否新车载(支持例保一程一检)
    is_new_cz = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="是否新车载",
        help_text="是否新车载(支持例保一程一检):0否,1是"
    )

    # 是否无障碍
    has_wheelchair = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="是否无障碍",
        help_text="是否无障碍:0否,1是"
    )

    # 是否外公司共营车辆
    is_share = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="是否共营车辆",
        help_text="是否外公司共营车辆:0否,1是"
    )

    # 牌照号
    vehicle_plate = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="牌照号",
        help_text="牌照号"
    )

    # 自编号
    vehicle_no = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="自编号",
        help_text="自编号"
    )

    # 车辆型号
    vehicle_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="车辆型号",
        help_text="车辆型号"
    )

    # 车型简称
    car_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="车型简称",
        help_text="车型简称",
        db_comment="车型简称"
    )

    # 客车类型
    bus_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="客车类型",
        help_text="客车类型"
    )

    # 燃料种类
    fuel_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="燃料种类",
        help_text="燃料种类"
    )

    # 排放等级
    emission_class = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="排放等级",
        help_text="排放等级"
    )

    # 购买日期
    buy_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="购买日期",
        help_text="购买日期"
    )

    # 报废年限
    scrap_years = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="报废年限",
        help_text="报废年限(年)"
    )

    # 计划报废年份
    plan_scrap_year = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="计划报废年份",
        help_text="计划报废年份"
    )

    # 实际报废或转籍日期
    actual_scrap_year = models.DateField(
        null=True,
        blank=True,
        verbose_name="实际报废日期",
        help_text="实际报废或转籍日期"
    )

    # 额定载客人数
    passenger_number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="额定载客人数",
        help_text="额定载客人数"
    )

    # 车辆座位数
    seats_number = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="车辆座位数",
        help_text="车辆座位数"
    )

    # 车辆尺寸
    size = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="车辆尺寸",
        help_text="车辆尺寸"
    )

    # 发动机位置
    engine_position = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="发动机位置",
        help_text="发动机位置"
    )

    # 发动机型号
    engine_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="发动机型号",
        help_text="发动机型号"
    )

    # 有无空调
    have_air_condition = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="有无空调",
        help_text="有无空调:0无,1有"
    )

    # 有无后置摄像头
    have_back_camera = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="有无后置摄像头",
        help_text="有无后置摄像头:0无,1有"
    )

    # 高等级车
    is_high_grade = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="高等级车",
        help_text="高等级车:0否,1是"
    )

    # 智能化终端
    have_system = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="智能化终端",
        help_text="智能化终端"
    )

    # 车辆状态
    vehicle_condition = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="车辆状态",
        help_text="车辆状态"
    )

    # 实时状况
    realtime_condition = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="实时状况",
        help_text="实时状况"
    )

    # 备注
    remark = models.TextField(
        null=True,
        blank=True,
        verbose_name="备注",
        help_text="备注"
    )

    # 预计到站时间
    dzsj = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="预计到站时间",
        help_text="预计到站时间"
    )

    # POS机编号
    pos_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="POS机编号",
        help_text="POS机编号"
    )

    # 车载手机号
    mobile_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="车载手机号",
        help_text="车载手机号"
    )

    # 车辆品牌
    vehicle_brand = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="车辆品牌",
        help_text="车辆品牌"
    )

    # 报废年限
    retirement_time = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="报废年限",
        help_text="报废年限(年)"
    )

    # 车辆长度
    vehicle_size = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="车辆长度",
        help_text="车辆长度(米)"
    )

    # 电子路牌
    electronic_lupai = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="电子路牌",
        help_text="电子路牌"
    )

    # 车辆门数
    vehicle_door = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="车辆门数",
        help_text="车辆门数"
    )

    # 额定耗油
    rated_oil = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="额定耗油",
        help_text="额定耗油(升/百公里)"
    )

    # 状态
    vehicle_status = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="状态",
        help_text="状态"
    )

    # 是否报废
    is_baofei = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="是否报废",
        help_text="是否报废:0否,1是"
    )

    # 是否开通通话功能
    voice_card_enabled = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="是否开通通话功能",
        help_text="是否开通通话功能:0否,1是"
    )

    # 序列号
    sn = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="序列号",
        help_text="序列号"
    )

    # 是否开通视频功能
    video_enable = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="是否开通视频功能",
        help_text="是否开通视频功能:0否,1是"
    )

    # 是否有视频功能
    has_video = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="是否有视频功能",
        help_text="是否有视频功能:0否,1是"
    )

    # 是否改装过
    is_modified = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="是否改装过",
        help_text="是否改装过:0否,1是"
    )

    # 是否新能源车
    is_new_energy = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="是否新能源车",
        help_text="是否新能源车:0否,1是"
    )

    # 车载GPS供应商
    manufacturer = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="车载GPS供应商",
        help_text="车载GPS供应商"
    )

    # 是否是新车
    new_flag = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="是否是新车",
        help_text="是否是新车:0否,1是"
    )

    # 是否显示充电状态
    show_charge = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="是否显示充电状态",
        help_text="是否显示充电状态:0否,1是"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "vehicle"
        verbose_name = "车辆表"
        verbose_name_plural = verbose_name
        ordering = ['vehicle_plate']
