'''
Description: 
Version: 1.0
Autor: 王晨
Date: 2025-10-10 09:33:35
LastEditors: 王晨
LastEditTime: 2025-11-03 16:24:25
'''
"""
基础实体模型
用于定义业务相关的通用字段和功能
"""
from django.db import models
from django.utils import timezone
from django.db.models import Q
from datetime import date
from calendar import monthrange
from dvadmin.utils.models import CoreModel


class ValidPeriodQuerySet(models.QuerySet):
    """
    有效时间范围查询集
    提供 valid_period 方法，用于过滤 exec_day 和 expiry_day 范围内的数据
    """
    
    def valid_period(self, date=None):
        """
        过滤有效时间范围内的数据
        
        参数:
            date: 指定日期，默认为当前日期
        
        返回:
            只返回 exec_day <= date <= expiry_day 的数据
            如果 exec_day 为空，则只检查 expiry_day
            如果 expiry_day 为空，则只检查 exec_day
            如果两者都为空，则返回该记录
            
        注意:
            使用此方法的模型必须包含 exec_day 和 expiry_day 字段
        """
        if date is None:
            date = timezone.now().date()
        
        # 构建查询条件
        # 1. exec_day 为空或 exec_day <= date
        exec_condition = Q(exec_day__isnull=True) | Q(exec_day__lte=date)
        
        # 2. expiry_day 为空或 expiry_day >= date
        expiry_condition = Q(expiry_day__isnull=True) | Q(expiry_day__gte=date)
        
        # 同时满足两个条件
        return self.filter(exec_condition & expiry_condition)
    
    def valid_period_by_month(self, year, month):
        """
        按月份查询有效时间范围内的数据
        
        参数:
            year: 年份
            month: 月份 (1-12)
        
        返回:
            返回该月份最后一天有效的所有记录
            使用该月最后一天作为查询日期，确保返回唯一记录
            
        注意:
            使用此方法的模型必须包含 exec_day 和 expiry_day 字段
            
        示例:
            # 查询 2025-11 月份有效的线路
            roadlines = RoadlineModel.objects.valid_period_by_month(2025, 11)
        """
        # 计算该月的最后一天
        last_day = monthrange(year, month)[1]
        month_end = date(year, month, last_day)
        
        # 使用该月最后一天查询
        return self.valid_period(month_end)


class ValidPeriodManager(models.Manager):
    """
    有效时间范围管理器
    提供 valid_period 方法，用于过滤 exec_day 和 expiry_day 范围内的数据
    """
    
    def get_queryset(self):
        """返回自定义查询集"""
        return ValidPeriodQuerySet(self.model, using=self._db)
    
    def valid_period(self, date=None):
        """过滤有效时间范围内的数据"""
        return self.get_queryset().valid_period(date)
    
    def valid_period_by_month(self, year, month):
        """按月份查询有效时间范围内的数据"""
        return self.get_queryset().valid_period_by_month(year, month)


class BaseDataModel(CoreModel):
    """
    基础数据模型 - 包含业务通用字段
    继承自CoreModel，添加业务特定的通用字段
    """
    # 删除标记 (0=未删除, 1=已删除)
    delete_mark = models.IntegerField(
        default=0, 
        verbose_name="删除标记", 
        help_text="删除标记，0表示未删除，1表示已删除",
        null=True,
        blank=True,
        db_comment="删除标记，0表示未删除，1表示已删除"
    )
    
    # 启用标记 (0=禁用, 1=启用)
    enabled_mark = models.IntegerField(
        default=1, 
        verbose_name="启用标记", 
        help_text="启用标记，0表示禁用，1表示启用",
        null=True,
        blank=True,
        db_comment="启用标记，0表示禁用，1表示启用"
    )
    
    # 数据归属公司（参考 CoreModel.dept_belong_id 命名规范）
    company_belong_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="数据归属公司",
        help_text="数据归属公司",
        db_comment="数据归属公司"
    )

    # 数据归属代理商
    agent_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="数据归属代理商",
        help_text="关联代理商，NULL=自营数据，有值=代理商数据",
        db_comment="数据归属代理商ID，NULL=自营数据，有值=代理商数据"
    )

    # 创建人姓名 (字符串类型)
    creator_name = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="创建人姓名", 
        help_text="创建人姓名",
        db_comment="创建人姓名"
    )
     
    # 修改人姓名 (字符串类型)
    modifier_name = models.CharField(
        max_length=100, 
        null=True, 
        blank=True, 
        verbose_name="修改人姓名", 
        help_text="修改人姓名",
        db_comment="修改人姓名"
    )

    class Meta:
        abstract = True
        verbose_name = '基础数据模型'
        verbose_name_plural = verbose_name