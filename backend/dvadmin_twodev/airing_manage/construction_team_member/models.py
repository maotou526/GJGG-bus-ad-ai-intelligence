'''
Description: 施工团队成员模型
Version: 1.0
Autor: AI Assistant
Date: 2026-03-17
LastEditors:
LastEditTime: 2026-03-17
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.airing_manage.construction_team.models import ConstructionTeamModel
from conf.env import CUS_TABLE_PREFIX


class ConstructionTeamMemberModel(BaseDataModel):
    """
    施工团队成员模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 施工团队ID
    team_id = models.ForeignKey(
        ConstructionTeamModel,
        on_delete=models.PROTECT,
        db_column="team_id",
        db_constraint=False,
        null=False,
        blank=False,
        verbose_name="施工团队ID",
        help_text="关联施工团队表（dwd_construction_team）",
        db_comment="施工团队ID，关联施工团队表（dwd_construction_team）",
        related_name="members",
    )

    # 用户ID
    user_id = models.CharField(
        max_length=36,
        null=False,
        blank=False,
        verbose_name="用户ID",
        help_text="关联User表",
        db_comment="用户ID，关联User表"
    )

    # 用户名称
    user_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="用户名称",
        help_text="用户名称，冗余字段",
        db_comment="用户名称，冗余字段"
    )

    # 成员角色
    member_role = models.IntegerField(
        null=False,
        blank=False,
        verbose_name="成员角色",
        help_text="成员角色：1=负责人, 2=成员",
        db_comment="成员角色：1=负责人, 2=成员"
    )

    # 身份证号
    id_card = models.CharField(
        max_length=18,
        null=True,
        blank=True,
        verbose_name="身份证号",
        help_text="身份证号",
        db_comment="身份证号"
    )

    # 联系电话
    phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="联系电话",
        help_text="联系电话",
        db_comment="联系电话"
    )

    # 资质
    qualification = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="资质",
        help_text="资质信息",
        db_comment="资质信息"
    )

    # 工作年限
    work_years = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="工作年限",
        help_text="工作年限",
        db_comment="工作年限"
    )

    # 加入时间
    join_time = models.DateField(
        null=True,
        blank=True,
        verbose_name="加入时间",
        help_text="加入团队时间",
        db_comment="加入团队时间"
    )

    # 成员状态
    member_status = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        verbose_name="成员状态",
        help_text="成员状态：1=在职, 2=离职",
        db_comment="成员状态：1=在职, 2=离职"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "construction_team_member"
        verbose_name = "施工团队成员表"
        verbose_name_plural = verbose_name
        ordering = ["-create_datetime"]
        unique_together = [("team_id", "user_id")]
        indexes = [
            models.Index(fields=["team_id"]),
            models.Index(fields=["user_id"]),
            models.Index(fields=["member_role"]),
            models.Index(fields=["member_status"]),
        ]
