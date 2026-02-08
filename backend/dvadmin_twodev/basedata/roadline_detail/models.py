from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel, ValidPeriodManager
from dvadmin_twodev.basedata.roadline.models import RoadlineModel
from conf.env import CUS_TABLE_PREFIX


class RoadlineDetailModel(BaseDataModel):
    """
    线路走向详情模型
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 线路主表外键
    roadline = models.ForeignKey(
        RoadlineModel,
        on_delete=models.CASCADE,
        db_constraint=False,  # 不创建数据库外键约束
        null=True,
        blank=True,
        verbose_name="关联roadline表",
        help_text="关联的roadline表",
        related_name="details",
        db_comment="关联的roadline表"
    )
    
    # 上下行：0上行，1下行
    up_down = models.IntegerField(
        db_column='updown',
        null=True,
        blank=True,
        verbose_name="上下行",
        help_text="上下行：0上行，1下行",
        db_comment="上下行：0上行，1下行"
    )
    
    # 起点名称
    start_name = models.CharField(
        max_length=100,
        db_column='start_stop_name',
        null=True,
        blank=True,
        verbose_name="起点名称",
        help_text="起点名称",
        db_comment="起点名称"
    )
    
    # 开往方向
    to_direction = models.CharField(
        max_length=100,
        db_column='to_direction',
        null=True,
        blank=True,
        verbose_name="开往方向",
        help_text="开往方向",
        db_comment="开往方向"
    )
    
    # 线路走向
    line_direction = models.CharField(
        max_length=100,
        db_column='line_direction',
        null=True,
        blank=True,
        verbose_name="线路走向",
        help_text="线路走向",
        db_comment="线路走向"
    )
    
    # 首末班时间
    start_end_time = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="首末班时间",
        help_text="首末班时间（如：05:30-22:00）",
        db_comment="首末班时间（如：05:30-22:00）"
    )
    
    # 线路轨迹84坐标系
    lon_lat84 = models.TextField(
        null=True,
        blank=True,
        verbose_name="线路轨迹84坐标",
        help_text="WGS84坐标系线路轨迹数据",
        db_comment="WGS84坐标系线路轨迹数据"
    )
    
    # 线路轨迹02坐标系
    lon_lat02 = models.TextField(
        null=True,
        blank=True,
        verbose_name="线路轨迹02坐标",
        help_text="GCJ02坐标系线路轨迹数据",
        db_comment="GCJ02坐标系线路轨迹数据"
    )
    
    # 线路详情长度
    line_length = models.DecimalField(
        max_digits=15,   #这个值代表包含小数位数一共15位
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="线路详情长度",
        help_text="线路详情长度（km）",
        db_comment="线路详情长度（km）"
    )
    
    # 非直线系数
    non_linear_coefficient = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="非直线系数", 
        help_text="非直线系数（实际路径长度/直线距离）",
        db_comment="非直线系数（实际路径长度/直线距离）"
    )
    
    # 环域分布
    area = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="环域分布",
        help_text="线路覆盖的环域分布范围",
        db_comment="线路覆盖的环域分布范围"
    )
    
    # 途经POI
    poi = models.TextField(
        null=True,
        blank=True,
        verbose_name="途经POI",
        help_text="线路途经的兴趣点信息",
        db_comment="线路途经的兴趣点信息"
    )
    
    # 启用日期
    exec_day = models.DateField(
        null=True,
        blank=True,
        verbose_name="启用日期",
        help_text="启用日期",
        db_comment="启用日期"
    )
    
    # 截止日期
    expiry_day = models.DateField(
        db_column='expir_day',
        null=True,
        blank=True,
        verbose_name="截止日期",
        help_text="截止日期",
        db_comment="截止日期"
    )
    
    
    # 最大公交复线率（线路级别）
    max_roadline_overlap_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="最大公交复线率（线路级别）",
        help_text="最大公交复线率（百分比，0-100），用来记录数据的最大复线率",
        db_comment="最大公交复线率（百分比，0-100），用来记录数据的最大复线率"
    )

    # 使用有效时间范围管理器
    objects = ValidPeriodManager()
    
    class Meta:
        db_table = CUS_TABLE_PREFIX + "roadline_dtl"
        verbose_name = "线路走向详情表"
        verbose_name_plural = verbose_name
        ordering = ['roadline', 'up_down']