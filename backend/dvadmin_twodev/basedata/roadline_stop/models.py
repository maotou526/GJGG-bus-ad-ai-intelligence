
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel, ValidPeriodManager
from conf.env import CUS_TABLE_PREFIX

class RoadlineStopModel(BaseDataModel):
    """
    站点模型
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 站点编号
    stop_code = models.CharField(
        max_length=50,
        db_column='stop_code',
        null=True,
        blank=True,
        verbose_name="站点编号",
        help_text="站点编号"
    )
    
    # 环域
    area = models.CharField(
        max_length=100,
        db_column='area',
        null=True,
        blank=True,
        verbose_name="环域",
        help_text="环域",
        db_comment="环域"
    )
    
    # 区属
    district = models.CharField(
        max_length=100,
        db_column='district',
        null=True,
        blank=True,
        verbose_name="区属",
        help_text="区属",
        db_comment="区属"
    )
    
    # 道路名称
    roadline_name = models.CharField(
        max_length=200,
        db_column='roadline_name',
        null=True,
        blank=True,
        verbose_name="道路名称",
        help_text="道路名称"
    )
    
    # 街道
    street = models.CharField(
        max_length=200,
        db_column='street',
        null=True,
        blank=True,
        verbose_name="街道",
        help_text="街道"
    )
    
    # 站点名称
    stop_name = models.CharField(
        max_length=200,
        db_column='stop_name',
        null=True,
        blank=True,
        verbose_name="站点名称",
        help_text="站点名称"
    )
    
    # 拼音名称
    pinyin = models.CharField(
        max_length=200,
        db_column='pinyin',
        null=True,
        blank=True,
        verbose_name="拼音名称",
        help_text="站点名称的拼音"
    )
    
    # 路径方向
    path_direction = models.CharField(
        max_length=100,
        db_column='path_direction',
        null=True,
        blank=True,
        verbose_name="路径方向",
        help_text="路径方向"
    )
    
    # 站点地址
    stop_address = models.CharField(
        max_length=500,
        db_column='stop_address',
        null=True,
        blank=True,
        verbose_name="站点地址",
        help_text="站点详细地址"
    )
    
    # 线路列表
    road_line_list = models.TextField(
        db_column='road_line_list',
        null=True,
        blank=True,
        verbose_name="线路列表",
        help_text="经过该站点的线路列表"
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
        verbose_name="经度",
        help_text="WGS84坐标系经度"
    )
    
    # 纬度（WGS84坐标系）
    lat84 = models.DecimalField(
        max_digits=20,
        decimal_places=16,
        db_column='lat84',
        null=True,
        blank=True,
        verbose_name="纬度",
        help_text="WGS84坐标系纬度"
    )
    
    # 是否主干道
    is_main_road = models.BooleanField(
        db_column='is_main_road',
        default=False,
        null=True,
        blank=True,
        verbose_name="是否主干道",
        help_text="是否位于主干道：True是，False否"
    )
    
    # 人行道宽度
    sidewalk_width = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        db_column='sidewalk_width',
        null=True,
        blank=True,
        verbose_name="人行道宽度",
        help_text="人行道宽度（米）"
    )
    
    # 接驳地铁道路
    metroline_name = models.CharField(
        max_length=200,
        db_column='metroline_name',
        null=True,
        blank=True,
        verbose_name="接驳地铁道路",
        help_text="接驳的地铁线路名称"
    )
    
    # 启用日期
    exec_day = models.DateField(
        db_column='exec_day',
        null=True,
        blank=True,
        verbose_name="启用日期",
        help_text="启用日期"
    )
    
    # 截止日期
    expiry_day = models.DateField(
        db_column='expir_day',
        null=True,
        blank=True,
        verbose_name="截止日期",
        help_text="截止日期"
    )
    
    # 备注
    remark = models.TextField(
        db_column='remark',
        null=True,
        blank=True,
        verbose_name="备注",
        help_text="备注信息"
    )
    
    # 站点类型
    stop_type = models.IntegerField(
        db_column='stop_type',
        null=True,
        blank=True,
        verbose_name="站点类型",
        help_text="站点类型：1首末站，2枢纽站，3中途站，4无线路站",
        db_comment="站点类型：1首末站，2枢纽站，3中途站，4无线路站",
    )
    
    # 站点类型名称
    stop_type_name = models.CharField(
        max_length=50,
        db_column='stop_type_name',
        null=True,
        blank=True,
        verbose_name="站点类型名称",
        help_text="站点类型名称（如：首末站、枢纽站、中途站、无线路站）",
        db_comment="站点类型名称（如：首末站、枢纽站、中途站、无线路站）",
    )

    # 使用有效时间范围管理器
    objects = ValidPeriodManager()
    
    @classmethod
    def get_operating_count_by_month(cls, year, month):
        """
        获取指定月份有效的运营站点数量
        
        参数:
            year: 年份
            month: 月份 (1-12)
        
        返回:
            该月份最后一天有效的运营站点数量（delete_mark=0, enabled_mark=1）
            
        示例:
            count = RoadlineStopModel.get_operating_count_by_month(2025, 11)
        """
        return cls.objects.filter(
            delete_mark=0,
            enabled_mark=1
        ).valid_period_by_month(year, month).count()
    
    class Meta:
        db_table = CUS_TABLE_PREFIX + "roadline_stop"
        verbose_name = "站点表"
        verbose_name_plural = verbose_name
        ordering = ['stop_code']
