'''
Description: 会签模型
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 王晨
LastEditTime: 2026-01-21 17:10:44
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel


class WorkflowConfluenceModel(BaseDataModel):
    """
    会签模型
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
        help_text="节点ID，会签节点ID",
        db_comment="节点ID，会签节点ID"
    )
    
    # 表单节点ID
    form_node_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="表单节点ID",
        help_text="表单节点ID（可能与node_id不同，用于特殊场景）",
        db_comment="表单节点ID（可能与node_id不同，用于特殊场景）"
    )
    
    # 状态
    state = models.IntegerField(
        null=False,
        verbose_name="状态",
        help_text="状态，1=同意, 0=不同意（未处理时可能为NULL或0）",
        db_comment="状态，1=同意, 0=不同意（未处理时可能为NULL或0）"
    )
    
    class Meta:
        db_table = 'bs_nwf_confluence'
        verbose_name = "会签表"
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
        indexes = [
            models.Index(fields=['process_id'], name='idx_confluence_process_id'),
            models.Index(fields=['node_id'], name='idx_confluence_node_id'),
            models.Index(fields=['process_id', 'node_id'], name='idx_confluence_process_node'),
            models.Index(fields=['state'], name='idx_confluence_state'),
        ]
