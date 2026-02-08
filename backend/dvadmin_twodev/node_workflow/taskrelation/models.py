'''
Description: 任务执行人关系模型
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel


class WorkflowTaskRelationModel(BaseDataModel):
    """
    任务执行人关系模型
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """
    
    # 关联任务ID
    task_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="关联任务ID",
        help_text="关联任务ID，对应 lr_nwf_task.id",
        db_comment="关联任务ID，对应 lr_nwf_task.id"
    )
    
    # 用户ID
    user_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="用户ID",
        help_text="用户ID，执行人ID",
        db_comment="用户ID，执行人ID"
    )
    
    # 标记
    mark = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="标记",
        help_text="标记，0=需要处理, 1=暂时不需要处理",
        db_comment="标记，0=需要处理, 1=暂时不需要处理"
    )
    
    # 处理结果
    result = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="处理结果",
        help_text="处理结果，1=同意, 2=不同意, 0或NULL=未处理",
        db_comment="处理结果，1=同意, 2=不同意, 0或NULL=未处理"
    )
    
    # 排序号
    sort = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="排序号",
        help_text="排序号，串行会签时用于确定顺序",
        db_comment="排序号，串行会签时用于确定顺序"
    )
    
    # 处理时间
    time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="处理时间",
        help_text="处理时间",
        db_comment="处理时间"
    )
    
    class Meta:
        db_table = 'bs_nwf_taskrelation'
        verbose_name = "任务执行人关系表"
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
        indexes = [
            models.Index(fields=['task_id'], name='idx_taskrelation_task_id'),
            models.Index(fields=['user_id'], name='idx_taskrelation_user_id'),
            models.Index(fields=['task_id', 'user_id'], name='idx_taskrelation_task_user'),
            models.Index(fields=['mark'], name='idx_taskrelation_mark'),
        ]
