'''
Description: 流程任务模型
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 王晨
LastEditTime: 2026-01-21 17:10:35
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel


class WorkflowTaskModel(BaseDataModel):
    """
    流程任务模型
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
    
    # 节点ID
    node_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="节点ID",
        help_text="节点ID，对应流程模板中的节点ID",
        db_comment="节点ID，对应流程模板中的节点ID"
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
    
    # 任务类型
    type = models.IntegerField(
        null=False,
        verbose_name="任务类型",
        help_text="任务类型，1=审批, 2=传阅, 3=加签, 4=子流程, 5=重新创建",
        db_comment="任务类型，1=审批, 2=传阅, 3=加签, 4=子流程, 5=重新创建"
    )
    
    # 是否完成
    is_finished = models.IntegerField(
        null=False,
        verbose_name="是否完成",
        help_text="是否完成，1=完成, 2=关闭, 0=未完成",
        db_comment="是否完成，1=完成, 2=关闭, 0=未完成"
    )
    
    # 任务超时流转到下一个节点时间
    timeout_action = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="任务超时流转到下一个节点时间",
        help_text="任务超时流转到下一个节点时间",
        db_comment="任务超时流转到下一个节点时间"
    )
    
    # 任务超时提醒消息时间
    timeout_notice = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="任务超时提醒消息时间",
        help_text="任务超时提醒消息时间",
        db_comment="任务超时提醒消息时间"
    )
    
    # 任务超时消息提醒间隔时间
    timeout_interval = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="任务超时消息提醒间隔时间",
        help_text="任务超时消息提醒间隔时间",
        db_comment="任务超时消息提醒间隔时间"
    )
    
    # 任务超时策略
    timeout_strategy = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="任务超时策略",
        help_text="任务超时策略",
        db_comment="任务超时策略"
    )
    
    # 上一节点ID
    prev_node_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="上一节点ID",
        help_text="上一节点ID，记录流转路径",
        db_comment="上一节点ID，记录流转路径"
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
    # 是否被催办
    is_urge = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="是否被催办",
        help_text="是否被催办",
        db_comment="是否被催办"
    )
    
    # 第一个处理人ID
    first_user_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="第一个处理人ID",
        help_text="第一个处理人ID",
        db_comment="第一个处理人ID"
    )
    
    # 子流程ID
    child_process_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="子流程ID",
        help_text="子流程ID（如果是子流程任务）",
        db_comment="子流程ID（如果是子流程任务）"
    )
    
    # 批量审核
    is_batch_audit = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="批量审核",
        help_text="批量审核，1=是允许, 其他值都不允许",
        db_comment="批量审核，1=是允许, 其他值都不允许"
    )
    
    # 下一个节点是否已被审核
    is_next_audit = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="下一个节点是否已被审核",
        help_text="下一个节点是否已被审核",
        db_comment="下一个节点是否已被审核"
    )
    
    class Meta:
        db_table = 'bs_nwf_task'
        verbose_name = "流程任务表"
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
        indexes = [
            models.Index(fields=['process_id'], name='idx_task_process_id'),
            models.Index(fields=['node_id'], name='idx_task_node_id'),
            models.Index(fields=['is_finished'], name='idx_task_is_finished'),
        ]
