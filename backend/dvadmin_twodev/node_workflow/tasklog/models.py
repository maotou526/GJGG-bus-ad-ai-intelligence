'''
Description: 任务日志模型
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel


class WorkflowTaskLogModel(BaseDataModel):
    """
    任务日志模型
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
    
    # 操作码
    operation_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="操作码",
        help_text="操作码，agree/disagree/create/sign/revoke等",
        db_comment="操作码，agree/disagree/create/sign/revoke等"
    )
    
    # 操作名称
    operation_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="操作名称",
        help_text="操作名称，同意/不同意/创建/签名/撤销等",
        db_comment="操作名称，同意/不同意/创建/签名/撤销等"
    )
    
    # 节点ID
    node_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="节点ID",
        help_text="节点ID",
        db_comment="节点ID"
    )
    
    # 节点名称
    node_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="节点名称",
        help_text="节点名称",
        db_comment="节点名称"
    )
    
    # 流程任务类型
    task_type = models.IntegerField(
        null=False,
        verbose_name="流程任务类型",
        help_text="流程任务类型，0=创建, 1=审批, 2=传阅, 3=加签审核, 4=子流程, 5=重新创建",
        db_comment="流程任务类型，0=创建, 1=审批, 2=传阅, 3=加签审核, 4=子流程, 5=重新创建"
    )
    
    # 上一节点ID
    prev_node_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="上一节点ID",
        help_text="上一节点ID",
        db_comment="上一节点ID"
    )
    
    # 上一节点名称
    prev_node_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="上一节点名称",
        help_text="上一节点名称",
        db_comment="上一节点名称"
    )
    
    
    # 任务用户ID
    task_user_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="任务用户ID",
        help_text="任务用户ID（被处理任务的用户）",
        db_comment="任务用户ID（被处理任务的用户）"
    )
    
    # 任务用户姓名
    task_user_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="任务用户姓名",
        help_text="任务用户姓名",
        db_comment="任务用户姓名"
    )
    
    # 审批意见/描述
    des = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="审批意见",
        help_text="审批意见/描述",
        db_comment="审批意见/描述"
    )
    
    # 签名图片ID或路径
    sign_img = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="签名图片",
        help_text="签名图片ID或路径",
        db_comment="签名图片ID或路径"
    )
    
    # 印章图片ID或路径
    stamp_img = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="印章图片",
        help_text="印章图片ID或路径",
        db_comment="印章图片ID或路径"
    )
    
    class Meta:
        db_table = 'bs_nwf_tasklog'
        verbose_name = "任务日志表"
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
        indexes = [
            models.Index(fields=['process_id'], name='idx_tasklog_process_id'),
            models.Index(fields=['task_id'], name='idx_tasklog_task_id'),
        ]
