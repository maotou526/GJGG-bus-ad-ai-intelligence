'''
Description: 停车场站模型
Version: 1.0
Autor: 王晨
Date: 2025-10-18
LastEditors: 王晨
LastEditTime: 2025-10-27 14:05:36
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from conf.env import CUS_TABLE_PREFIX


class ParkModel(BaseDataModel):
    """
    停车场站模型
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

    # 场地编码
    park_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="场地编码",
        help_text="场地编码"
    )

    # 停车场地全称
    park_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="停车场地全称",
        help_text="停车场地全称"
    )

    # 停车场地地址
    park_address = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="停车场地地址",
        help_text="停车场地地址"
    )

    # 经度（GCJ02坐标系）
    lon02 = models.DecimalField(
        max_digits=20,
        decimal_places=16,
        db_column='lon02',
        null=True,
        blank=True,
        verbose_name="经度",
        help_text="GCJ02坐标系经度"
    )
    
    # 纬度（GCJ02坐标系）
    lat02 = models.DecimalField(
        max_digits=20,
        decimal_places=16,
        db_column='lat02',
        null=True,
        blank=True,
        verbose_name="纬度",
        help_text="GCJ02坐标系纬度"
    )

    # 经度（WGS84坐标系）
    lon84 = models.DecimalField(
        max_digits=20,
        decimal_places=16,
        db_column='lon84',
        null=True,
        blank=True,
        verbose_name="经度（WGS84）",
        help_text="WGS84坐标系经度"
    )
    
    # 纬度（WGS84坐标系）
    lat84 = models.DecimalField(
        max_digits=20,
        decimal_places=16,
        db_column='lat84',
        null=True,
        blank=True,
        verbose_name="纬度（WGS84）",
        help_text="WGS84坐标系纬度"
    )

    # 场地类型:0场内,1外停点,2终点站
    park_type = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="场地类型",
        help_text="场地类型:0场内,1外停点,2终点站"
    )

    # 停车场围栏
    park_fence = models.TextField(
        null=True,
        blank=True,
        verbose_name="停车场围栏",
        help_text="停车场围栏坐标数据"
    )

    # 是否有维修功能:0无,1有
    repair_flag = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="维修功能",
        help_text="是否有维修功能:0无,1有"
    )

    # 是否有报到设备:0无,1有
    report_flag = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="报到设备",
        help_text="是否有报到设备:0无,1有"
    )

    # 停车场状态:0停用,1建设中,2运营中
    park_status = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="停车场状态",
        help_text="停车场状态:0停用,1建设中,2运营中"
    )

    # 场站类型:0总站,1分站,2停车场,3维修中心
    station_type = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="场站类型",
        help_text="场站类型:0总站,1分站,2停车场,3维修中心"
    )

    # 总面积(平方米)
    total_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="总面积",
        help_text="总面积(平方米)"
    )

    # 建筑面积(平方米)
    building_area = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="建筑面积",
        help_text="建筑面积(平方米)"
    )

    # 停车位数量
    parking_space = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="停车位数量",
        help_text="停车位数量"
    )

    # 维修工位数量
    repair_space = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="维修工位数量",
        help_text="维修工位数量"
    )

    # 加油站数量
    gas_station_count = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="加油站数量",
        help_text="加油站数量"
    )

    # 充电桩数量
    charging_pile_count = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="充电桩数量",
        help_text="充电桩数量"
    )

    # 洗车位数量
    car_wash_count = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="洗车位数量",
        help_text="洗车位数量"
    )

    # 设施配置标记
    # 办公楼:0无,1有
    office_flag = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="办公楼",
        help_text="办公楼:0无,1有"
    )

    # 食堂:0无,1有
    canteen_flag = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="食堂",
        help_text="食堂:0无,1有"
    )

    # 宿舍:0无,1有
    dormitory_flag = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="宿舍",
        help_text="宿舍:0无,1有"
    )

    # 保安室:0无,1有
    security_room_flag = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="保安室",
        help_text="保安室:0无,1有"
    )

    # 仓库:0无,1有
    warehouse_flag = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="仓库",
        help_text="仓库:0无,1有"
    )

    # 培训室:0无,1有
    training_room_flag = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="培训室",
        help_text="培训室:0无,1有"
    )

    # 运营信息
    # 场站运营开始时间
    oper_start_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="运营开始时间",
        help_text="场站运营开始时间"
    )

    # 场站运营结束时间
    oper_end_time = models.TimeField(
        null=True,
        blank=True,
        verbose_name="运营结束时间",
        help_text="场站运营结束时间"
    )

    # 负责人
    principal = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="负责人",
        help_text="负责人"
    )

    # 联系电话
    contact_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="联系电话",
        help_text="联系电话"
    )

    # 电子邮箱
    contact_email = models.EmailField(
        null=True,
        blank=True,
        verbose_name="电子邮箱",
        help_text="电子邮箱"
    )

    @classmethod
    def get_operating_count(cls):
        """
        获取运营场站数量
        
        返回:
            启用的运营场站数量（delete_mark=0, enabled_mark=1）
            
        示例:
            count = ParkModel.get_operating_count()
        """
        return cls.objects.filter(
            delete_mark=0,
            enabled_mark=1
        ).count()
    
    class Meta:
        db_table = CUS_TABLE_PREFIX + "park"
        verbose_name = "停车场站表"
        verbose_name_plural = verbose_name
        ordering = ['park_name']
