"""
Description: 上刊施工人员模型
Version: 1.0
"""
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.airing_manage.on_air_order.models import OnAirOrderModel
from conf.env import CUS_TABLE_PREFIX


class OnAirWorkerModel(BaseDataModel):
    """
    上刊施工人员模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 上刊订单ID
    order_id = models.ForeignKey(
        OnAirOrderModel,
        on_delete=models.PROTECT,
        db_column="order_id",
        db_constraint=False,
        related_name="workers",
        verbose_name="上刊订单ID",
        help_text="关联上刊订单",
        db_comment="上刊订单ID，关联上刊订单表"
    )

    # 用户ID
    user_id = models.CharField(
        max_length=36,
        verbose_name="用户ID",
        help_text="关联User表",
        db_comment="用户ID，关联User表"
    )

    # 用户姓名
    user_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="用户姓名",
        help_text="用户姓名",
        db_comment="用户姓名，冗余字段"
    )

    # 施工队伍ID
    team_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        verbose_name="施工队伍ID",
        help_text="关联ConstructionTeamModel",
        db_comment="施工队伍ID，关联施工队伍表"
    )

    # 施工队伍名称
    team_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="施工队伍名称",
        help_text="施工队伍名称",
        db_comment="施工队伍名称，冗余字段"
    )

    # 人员角色
    person_role = models.IntegerField(
        verbose_name="人员角色",
        help_text="1:施工负责人, 2:施工人员",
        db_comment="人员角色：1=施工负责人, 2=施工人员"
    )

    # 预计进场时间
    expected_entry_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="预计进场时间",
        help_text="预计进场时间",
        db_comment="预计进场时间"
    )

    # 预计离场时间
    expected_exit_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="预计离场时间",
        help_text="预计离场时间",
        db_comment="预计离场时间"
    )

    # 实际进场时间
    actual_entry_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="实际进场时间",
        help_text="实际进场时间",
        db_comment="实际进场时间"
    )

    # 实际离场时间
    actual_exit_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="实际离场时间",
        help_text="实际离场时间",
        db_comment="实际离场时间"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "on_air_worker"
        verbose_name = "上刊施工人员"
        verbose_name_plural = verbose_name
        ordering = ["-create_datetime"]
        unique_together = [("order_id", "user_id")]
        indexes = [
            models.Index(fields=["order_id"], name="idx_oaw_order_id"),
            models.Index(fields=["user_id"], name="idx_oaw_user_id"),
            models.Index(fields=["person_role"], name="idx_oaw_person_role"),
        ]

    def __str__(self):
        return f"{self.user_name or self.user_id} - 角色{self.person_role}"
