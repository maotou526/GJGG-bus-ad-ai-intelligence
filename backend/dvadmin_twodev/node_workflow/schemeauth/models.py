'''
Description: 流程模板权限模型
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel


class WorkflowSchemeAuthModel(BaseDataModel):
    """
    流程模板权限模型
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """
    
    # 关联流程信息表ID
    scheme_info_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="关联流程信息表ID",
        help_text="关联流程信息表ID，对应 lr_nwf_schemeinfo.id",
        db_comment="关联流程信息表ID，对应 lr_nwf_schemeinfo.id"
    )
    
    # 对应对象类型
    obj_type = models.IntegerField(
        null=False,
        verbose_name="对应对象类型",
        help_text="对应对象类型，1=岗位, 2=角色, 3=用户, 4=所有人可看",
        db_comment="对应对象类型，1=岗位, 2=角色, 3=用户, 4=所有人可看"
    )
    
    # 对象ID
    obj_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="对象ID",
        help_text="对象ID（岗位ID/角色ID/用户ID），obj_type=4时为空",
        db_comment="对象ID（岗位ID/角色ID/用户ID），obj_type=4时为空"
    )
    
    # 对象名称
    obj_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="对象名称",
        help_text="对象名称，冗余字段便于显示",
        db_comment="对象名称，冗余字段便于显示"
    )
    
    class Meta:
        db_table = 'bs_nwf_schemeauth'
        verbose_name = "流程模板权限表"
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
        indexes = [
            models.Index(fields=['scheme_info_id'], name='idx_schemeauth_scheme_info_id'),
            models.Index(fields=['obj_type', 'obj_id'], name='idx_schemeauth_obj'),
        ]
