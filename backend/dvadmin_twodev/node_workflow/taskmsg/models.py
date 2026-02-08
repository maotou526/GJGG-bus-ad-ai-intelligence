'''
Description: 任务消息模型
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel


class WorkflowTaskMsgModel(BaseDataModel):
    """
    任务消息模型
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """
    
    # 关联流程进程ID
    process_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="关联流程进程ID",
        help_text="关联流程进程ID，对应 lr_nwf_process.id",
        db_comment="关联流程进程ID，对应 lr_nwf_process.id"
    )
    
    # 任务ID
    task_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="任务ID",
        help_text="任务ID，对应 lr_nwf_task.id",
        db_comment="任务ID，对应 lr_nwf_task.id"
    )
    
    # 发送人用户ID
    from_user_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="发送人用户ID",
        help_text="发送人用户ID",
        db_comment="发送人用户ID"
    )
    
    # 发送人账号
    from_user_account = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="发送人账号",
        help_text="发送人账号",
        db_comment="发送人账号"
    )
    
    # 发送人姓名
    from_user_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="发送人姓名",
        help_text="发送人姓名",
        db_comment="发送人姓名"
    )
    
    # 接收人用户ID
    to_user_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="接收人用户ID",
        help_text="接收人用户ID",
        db_comment="接收人用户ID"
    )
    
    # 接收人账号
    to_account = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="接收人账号",
        help_text="接收人账号",
        db_comment="接收人账号"
    )
    
    # 接收人姓名
    to_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="接收人姓名",
        help_text="接收人姓名",
        db_comment="接收人姓名"
    )
    
    # 消息标题
    title = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="消息标题",
        help_text="消息标题",
        db_comment="消息标题"
    )
    
    # 消息内容
    content = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="消息内容",
        help_text="消息内容，通知的具体内容",
        db_comment="消息内容，通知的具体内容"
    )
    
    # 是否结束
    is_finished = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="是否结束",
        help_text="是否结束，1=结束, 0=未结束",
        db_comment="是否结束，1=结束, 0=未结束"
    )
    
    class Meta:
        db_table = 'bs_nwf_taskmsg'
        verbose_name = "任务消息表"
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
        indexes = [
            models.Index(fields=['process_id'], name='idx_taskmsg_process_id'),
            models.Index(fields=['task_id'], name='idx_taskmsg_task_id'),
            models.Index(fields=['to_user_id'], name='idx_taskmsg_to_user_id'),
            models.Index(fields=['is_finished'], name='idx_taskmsg_is_finished'),
        ]
