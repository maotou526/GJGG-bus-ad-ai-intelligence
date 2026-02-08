'''
Description: 流程模板信息模型
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel


class WorkflowSchemeInfoModel(BaseDataModel):
    """
    流程模板信息模型
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """
    
    # 流程编号
    code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="流程编号",
        help_text="流程编号，唯一标识",
        db_comment="流程编号，唯一标识"
    )
    
    # 流程名称
    name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="流程名称",
        help_text="流程名称",
        db_comment="流程名称"
    )
    
    # 流程分类
    category = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="流程分类",
        help_text="流程分类",
        db_comment="流程分类"
    )
    
    # 当前启用版本的模板ID
    scheme_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="当前启用版本的模板ID",
        help_text="当前启用版本的模板ID，关联 lr_nwf_scheme.id",
        db_comment="当前启用版本的模板ID，关联 lr_nwf_scheme.id"
    )
    
    # 是否有效（注意：这个字段在BaseDataModel中已有enabled_mark，但数据库字段不同）
    # 这里需要覆盖或使用不同的字段名映射
    # enabled_mark 在BaseDataModel中已定义，但数据库字段为F_EnabledMark，符合要求
    
    # 是否在我的任务允许发起
    mark = models.IntegerField(
        null=False,
        verbose_name="是否允许发起",
        help_text="是否在我的任务允许发起，1=允许, 2=不允许",
        db_comment="是否在我的任务允许发起，1=允许, 2=不允许"
    )
    
    # 是否在App上允许发起
    is_in_app = models.IntegerField(
        null=False,
        verbose_name="是否在App上允许发起",
        help_text="是否在App上允许发起，1=允许, 2=不允许",
        db_comment="是否在App上允许发起，1=允许, 2=不允许"
    )
    
    # 描述信息
    description = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="描述信息",
        help_text="描述信息",
        db_comment="描述信息"
    )
    
    class Meta:
        db_table = 'bs_nwf_schemeinfo'
        verbose_name = "流程模板信息表"
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
        indexes = [
            models.Index(fields=['code'], name='idx_schemeinfo_code'),
            models.Index(fields=['scheme_id'], name='idx_schemeinfo_scheme_id'),
        ]
