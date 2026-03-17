'''
Description: 施工团队模型
Version: 1.0
Autor: AI Assistant
Date: 2026-03-17
LastEditors:
LastEditTime: 2026-03-17
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from conf.env import CUS_TABLE_PREFIX


class ConstructionTeamModel(BaseDataModel):
    """
    施工团队模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 团队编号
    team_no = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        unique=True,
        verbose_name="团队编号",
        help_text="团队唯一编号",
        db_comment="团队编号，唯一编号"
    )

    # 团队名称
    team_name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="团队名称",
        help_text="团队名称",
        db_comment="团队名称"
    )

    # 团队类型
    team_type = models.IntegerField(
        null=False,
        blank=False,
        verbose_name="团队类型",
        help_text="团队类型：1=自营团队, 2=代理商团队",
        db_comment="团队类型：1=自营团队, 2=代理商团队"
    )

    # 联系电话
    contact_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="联系电话",
        help_text="联系电话",
        db_comment="联系电话"
    )

    # 备注
    remark = models.TextField(
        null=True,
        blank=True,
        verbose_name="备注",
        help_text="备注",
        db_comment="备注"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "construction_team"
        verbose_name = "施工团队表"
        verbose_name_plural = verbose_name
        ordering = ["-create_datetime"]
        indexes = [
            models.Index(fields=["team_no"]),
            models.Index(fields=["team_type"]),
        ]
