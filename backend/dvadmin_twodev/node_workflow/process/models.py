'''
Description: 流程进程模型
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 王晨
LastEditTime: 2026-01-21 17:10:50
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel


class WorkflowProcessModel(BaseDataModel):
    """
    流程进程模型
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """
    
    # 流程模板ID
    scheme_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="流程模板ID",
        help_text="流程模板ID，关联 lr_nwf_scheme.id",
        db_comment="流程模板ID，关联 lr_nwf_scheme.id"
    )
    
    # 流程编号
    scheme_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="流程编号",
        help_text="流程编号，冗余字段",
        db_comment="流程编号，冗余字段"
    )
    
    # 流程名称
    scheme_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="流程名称",
        help_text="流程名称，冗余字段",
        db_comment="流程名称，冗余字段"
    )
    
    # 流程标题
    title = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="流程标题",
        help_text="流程标题，本次流程的具体标题",
        db_comment="流程标题，本次流程的具体标题"
    )
    
    # 流程进程等级
    level = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="流程进程等级",
        help_text="流程进程等级，1=普通, 2=重要, 3=紧急",
        db_comment="流程进程等级，1=普通, 2=重要, 3=紧急"
    )
    
    # 流程进程有效标志（注意：BaseDataModel已有enabled_mark，但这里的语义不同）
    # 这里需要覆盖或使用不同的字段名映射
    # 数据库字段为F_EnabledMark，但这里的业务含义是：1=正常, 2=草稿, 3=作废
    # enabled_mark 在BaseDataModel中已定义，但数据库字段为F_EnabledMark，符合要求
    
    # 是否重新发起
    is_again = models.IntegerField(
        null=False,
        verbose_name="是否重新发起",
        help_text="是否重新发起，1=是, 0=不是",
        db_comment="是否重新发起，1=是, 0=不是"
    )
    
    # 流程进程是否结束
    is_finished = models.IntegerField(
        null=False,
        verbose_name="流程进程是否结束",
        help_text="流程进程是否结束，1=是, 0=不是",
        db_comment="流程进程是否结束，1=是, 0=不是"
    )
    
    # 是否是子流程进程
    is_child = models.IntegerField(
        null=False,
        verbose_name="是否是子流程进程",
        help_text="是否是子流程进程，1=是, 0=不是",
        db_comment="是否是子流程进程，1=是, 0=不是"
    )
    
    # 子流程执行方式
    is_asyn = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="子流程执行方式",
        help_text="子流程执行方式，0=同步, 1=异步",
        db_comment="子流程执行方式，0=同步, 1=异步"
    )
    
    # 父节点ID
    parent_node_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="父节点ID",
        help_text="父节点ID，父流程中发起子流程的节点ID",
        db_comment="父节点ID，父流程中发起子流程的节点ID"
    )
    
    # 父任务ID
    parent_task_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="父任务ID",
        help_text="父任务ID，父流程中发起子流程的任务ID",
        db_comment="父任务ID，父流程中发起子流程的任务ID"
    )
    
    # 父流程ID
    parent_process_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="父流程ID",
        help_text="父流程ID，子流程时关联父流程",
        db_comment="父流程ID，子流程时关联父流程"
    )
    
    
    # 是否开始处理
    is_start = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="是否开始处理",
        help_text="是否开始处理，1=表示开始处理过了, 0=还没人处理过",
        db_comment="是否开始处理，1=表示开始处理过了, 0=还没人处理过"
    )


    
    class Meta:
        db_table = 'bs_nwf_process'
        verbose_name = "流程进程表"
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
        indexes = [
            models.Index(fields=['scheme_id'], name='idx_process_scheme_id'),
            models.Index(fields=['scheme_code'], name='idx_process_scheme_code'),
            models.Index(fields=['creator'], name='idx_process_creator'),
            models.Index(fields=['is_finished'], name='idx_process_is_finished'),
            models.Index(fields=['parent_process_id'], name='idx_process_parent_process_id'),
        ]
