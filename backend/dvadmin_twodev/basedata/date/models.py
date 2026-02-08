'''
Description: 基础日期管理模型
Version: 1.0
Autor: 王晨
Date: 2025-10-23
LastEditors: 王晨
LastEditTime: 2025-10-23
'''
import calendar
from django.db import models
from dvadmin.utils.models import CoreModel
from conf.env import CUS_TABLE_PREFIX


class BaseDateModel(CoreModel):
    """
    基础日期管理模型
    用于管理工作日、周末、节假日等日期信息
    """
    
    date = models.DateField(
        verbose_name='日期',
        help_text='日期',
        unique=True,
        db_index=True
    )
    
    month = models.IntegerField(
        verbose_name='当月',
        help_text='当月(1-12)',
        null=True,
        blank=True
    )
    
    count = models.IntegerField(
        verbose_name='当月天数',
        help_text='当月天数(28-31)',
        null=True,
        blank=True
    )
    
    date_type = models.IntegerField(
        verbose_name='日期类型',
        help_text='日期类型(0:工作日 1:休息日)',
        default=0,
        db_index=True
    )
    
    name = models.CharField(
        max_length=100,
        verbose_name='名称',
        help_text='节假日名称或特殊日期名称',
        null=True,
        blank=True
    )
    
    week = models.IntegerField(
        verbose_name='星期几',
        help_text='星期几(0-6, 0为星期日，1为星期一)',
        null=True,
        blank=True
    )
    
    is_work = models.IntegerField(
        verbose_name='是否上班',
        help_text='是否上班(节假日调休标记)',
        default=1
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "base_date"
        verbose_name = "基础日期"
        verbose_name_plural = verbose_name
        ordering = ['-date']

    def __str__(self):
        type_display = {0: '工作日', 1: '休息日'}.get(self.date_type, '未知')
        return f"{self.date} - {type_display}"
    
    def save(self, *args, **kwargs):
        """
        保存时自动计算月份、当月天数和星期
        """
        if self.date:
            # 自动设置月份
            if not self.month:
                self.month = self.date.month
            
            # 自动设置当月天数
            if not self.count:
                self.count = calendar.monthrange(self.date.year, self.date.month)[1]
            
            # 自动设置星期(Python weekday: 0=Monday, 6=Sunday)
            # 转换为 0-6 (0=Sunday, 1=Monday)
            if self.week is None:
                python_weekday = self.date.weekday()  # 0=Monday, 6=Sunday
                self.week = (python_weekday + 1) % 7  # 转换为 0=Sunday, 1=Monday
        
        super().save(*args, **kwargs)
