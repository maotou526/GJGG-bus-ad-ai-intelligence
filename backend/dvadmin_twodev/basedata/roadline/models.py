'''
Description: 线路模型
Version: 1.0
Autor: 王晨
Date: 2025-10-09 17:32:55
LastEditors: 王晨
LastEditTime: 2025-12-16 14:14:00
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel, ValidPeriodManager
from conf.env import CUS_TABLE_PREFIX

class RoadlineModel(BaseDataModel):
    """
    线路模型
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 公司编码
    company_code = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        verbose_name="公司编码", 
        help_text="公司编码",
        db_comment="公司编码"
    )
    
    # 公司名称
    company_name = models.CharField(
        max_length=200, 
        null=True, 
        blank=True, 
        verbose_name="公司名称", 
        help_text="公司名称",
        db_comment="公司名称"
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
    
    # 企业线路编码
    normal_code = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        verbose_name="企业线路编码", 
        help_text="企业线路编码",
        db_comment="企业线路编码"
    )
    
    # 行业线路编号
    ygc_code = models.CharField(
        max_length=50, 
        null=True, 
        blank=True, 
        verbose_name="行业线路编号", 
        help_text="行业线路编号",
        db_comment="行业线路编号"
    )
    
    # 线路名称
    line_name = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="线路名称", 
        help_text="线路名称",
        db_comment="线路名称"
    )
    
    # 线路平均长度
    line_length = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name="线路平均长度", 
        help_text="线路平均长度（km）",
        db_comment="线路平均长度（km）"
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
    
    # 线路类型：0普通，1挂牌线，2区间，3同名区间，4定班线，5定制公交，6高峰线，7夜宵线，8低谷定班线
    line_type = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="线路类型", 
        help_text="线路类型：0普通，1挂牌线，2区间，3同名区间，4定班线，5定制公交，6高峰线，7夜宵线，8低谷定班线",
        db_comment="线路类型：0普通，1挂牌线，2区间，3同名区间，4定班线，5定制公交，6高峰线，7夜宵线，8低谷定班线"
    )
    
    # 售票方式：1无人，2有人
    sell_type = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="售票方式", 
        help_text="售票方式：1无人，2有人",
        db_comment="售票方式：1无人，2有人"
    )
    
    # 票价类型：1单一，2多级
    ticket_price_type = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="票价类型", 
        help_text="票价类型：1单一，2多级",
        db_comment="票价类型：1单一，2多级"
    )
    
    # 票价
    ticket_price = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="票价", 
        help_text="票价（元），支持复杂票价描述",
        db_comment="票价（元），支持复杂票价描述"
    )
    
    # 运营时段分类：1全日线，2高峰线，3夜宵线
    yy_type = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="运营时段分类", 
        help_text="运营时段分类：1全日线，2高峰线，3夜宵线",
        db_comment="运营时段分类：1全日线，2高峰线，3夜宵线"
    )
    
    # 挂牌类型：1无，2全日挂牌，3高峰挂牌
    listing_type = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="挂牌类型", 
        help_text="挂牌类型：1无，2全日挂牌，3高峰挂牌",
        db_comment="挂牌类型：1无，2全日挂牌，3高峰挂牌"
    )
    
    # 定班类型：1无，2定班线
    schedule_type = models.IntegerField(
        null=True, 
        blank=True, 
        verbose_name="定班类型", 
        help_text="定班类型：1无，2定班线",
        db_comment="定班类型：1无，2定班线"
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
        null=True, 
        blank=True, 
        verbose_name="截止日期", 
        help_text="截止日期",
        db_comment="截止日期"
    )
    
    # 线路是否变更判断标识
    md5_hash = models.CharField(
        max_length=32, 
        null=True, 
        blank=True, 
        verbose_name="MD5标识", 
        help_text="线路是否变更判断标识",
        db_comment="线路是否变更判断标识"
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
    
    # 配车数
    bus_count = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="配车数",
        help_text="线路配置车辆总数",
        db_comment="线路配置车辆总数"
    )
    
    # 广告车辆数
    ad_bus_count = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="广告车辆数",
        help_text="可用于广告投放的车辆数",
        db_comment="可用于广告投放的车辆数"
    )
    
    # 覆盖人群
    covered_population = models.TextField(
        null=True,
        blank=True,
        verbose_name="覆盖人群",
        help_text="描述或标签，如'白领, 学生'",
        db_comment="描述或标签，如'白领, 学生'"
    )

    # 使用有效时间范围管理器
    objects = ValidPeriodManager()
    
    @classmethod
    def get_operating_count_by_month(cls, year, month):
        """
        获取指定月份有效的运营线路数量
        
        参数:
            year: 年份
            month: 月份 (1-12)
        
        返回:
            该月份最后一天有效的运营线路数量（delete_mark=0, enabled_mark=1）
            
        示例:
            count = RoadlineModel.get_operating_count_by_month(2025, 11)
        """
        return cls.objects.filter(
            delete_mark=0,
            enabled_mark=1
        ).valid_period_by_month(year, month).count()
    
    class Meta:
        db_table = CUS_TABLE_PREFIX + "roadline"
        verbose_name = "线路表"
        verbose_name_plural = verbose_name
        ordering = ['line_name']