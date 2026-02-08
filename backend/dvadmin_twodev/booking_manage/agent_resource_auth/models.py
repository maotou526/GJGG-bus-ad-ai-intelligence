'''
Description: 代理商资源授权模型
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.booking_manage.agent.models import AgentModel
from conf.env import CUS_TABLE_PREFIX


class AgentResourceAuthModel(BaseDataModel):
    """
    代理商资源授权模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 代理商ID
    agent_id = models.ForeignKey(
        AgentModel,
        on_delete=models.CASCADE,
        db_column='agent_id',  # 明确指定数据库列名
        db_constraint=False,  # 不创建数据库外键约束
        null=False,
        blank=False,
        verbose_name="代理商ID",
        help_text="关联代理商表",
        db_comment="代理商ID，关联代理商表"
    )

    # 资源类型
    resource_type = models.IntegerField(
        null=False,
        blank=False,
        verbose_name="资源类型",
        help_text="资源类型：1=线路, 2=车辆, 3=媒体类型",
        db_comment="资源类型：1=线路, 2=车辆, 3=媒体类型"
    )

    # 资源ID（UUID字符串，关联线路/车辆/媒体类型等表）
    resource_id = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        verbose_name="资源ID",
        help_text="资源对象ID（根据类型关联不同表，支持UUID）",
        db_comment="资源ID，资源对象ID（根据类型关联不同表，支持UUID）"
    )

    # 授权开始日期
    auth_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="授权开始日期",
        help_text="授权有效期起始",
        db_comment="授权开始日期，授权有效期起始"
    )

    # 授权结束日期
    auth_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="授权结束日期",
        help_text="授权有效期结束",
        db_comment="授权结束日期，授权有效期结束"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "agent_resource_auth"
        verbose_name = "代理商资源授权表"
        verbose_name_plural = verbose_name
        ordering = ['agent_id', 'resource_type', 'resource_id']
        # 组合唯一索引：代理商 + 资源类型 + 资源ID = 唯一的授权记录
        unique_together = [['agent_id', 'resource_type', 'resource_id']]
        indexes = [
            models.Index(fields=['agent_id', 'resource_type', 'resource_id']),
            models.Index(fields=['agent_id']),
            models.Index(fields=['resource_type', 'resource_id']),
            models.Index(fields=['auth_start_date', 'auth_end_date']),
        ]
