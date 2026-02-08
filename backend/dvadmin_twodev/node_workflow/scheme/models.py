'''
Description: 流程模板模型
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 王晨
LastEditTime: 2026-01-22 15:35:00
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.node_workflow.schemeinfo.models import WorkflowSchemeInfoModel


class WorkflowSchemeModel(BaseDataModel):
    """
    流程模板模型（版本管理）
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """
    
    # 关联流程信息表ID (外键关联)
    scheme_info = models.ForeignKey(
        WorkflowSchemeInfoModel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name="关联流程信息",
        help_text="关联流程信息表，对应 bs_nwf_schemeinfo",
        db_comment="关联流程信息表，对应 bs_nwf_schemeinfo",
        related_name="schemes",
        db_column="scheme_info_id"
    )
    
    # 模板类型
    type = models.IntegerField(
        null=False,
        verbose_name="模板类型",
        help_text="模板类型，1=正式, 2=草稿",
        db_comment="模板类型，1=正式, 2=草稿"
    )
    
    # 流程内容
    content = models.TextField(
        null=True,
        blank=True,
        verbose_name="流程内容",
        help_text="流程内容，存储流程节点和连线的完整配置（JSON格式）",
        db_comment="流程内容，存储流程节点和连线的完整配置（JSON格式）"
    )
    
    class Meta:
        db_table = 'bs_nwf_scheme'
        verbose_name = "流程模板表"
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
        indexes = [
            models.Index(fields=['scheme_info_id'], name='idx_scheme_scheme_info_id'),
            models.Index(fields=['type'], name='idx_scheme_type'),
        ]
