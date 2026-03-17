"""
Description: 进场登记模型
Version: 1.0
"""
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from conf.env import CUS_TABLE_PREFIX


class EntryRegModel(BaseDataModel):
    """
    进场登记模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 任务类型
    task_type = models.IntegerField(
        verbose_name="任务类型",
        help_text="1:上刊, 2:下刊",
        db_comment="任务类型：1=上刊, 2=下刊"
    )

    # 任务ID
    task_id = models.CharField(
        max_length=36,
        verbose_name="任务ID",
        help_text="关联上刊订单ID或下刊订单ID",
        db_comment="任务ID，关联上刊订单ID或下刊订单ID"
    )

    # 施工队伍车辆ID
    team_vehicle_id = models.CharField(
        max_length=36,
        verbose_name="施工队伍车辆ID",
        help_text="关联ConstructionTeamVehicleModel",
        db_comment="施工队伍车辆ID，关联施工队伍车辆表"
    )

    # 车牌号
    plate_no = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="车牌号",
        help_text="车牌号",
        db_comment="车牌号"
    )

    # 施工负责人ID
    leader_id = models.CharField(
        max_length=36,
        verbose_name="施工负责人ID",
        help_text="关联ConstructionTeamMemberModel",
        db_comment="施工负责人ID，关联施工队伍成员表"
    )

    # 施工负责人姓名
    leader_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="施工负责人姓名",
        help_text="施工负责人姓名",
        db_comment="施工负责人姓名，冗余字段"
    )

    # 施工负责人电话
    leader_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="施工负责人电话",
        help_text="施工负责人电话",
        db_comment="施工负责人电话"
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

    # 进场二维码图片
    qr_code_image = models.TextField(
        null=True,
        blank=True,
        verbose_name="进场二维码图片",
        help_text="Base64编码的进场二维码图片",
        db_comment="Base64编码的进场二维码图片"
    )

    # 登记时间
    register_time = models.DateTimeField(
        verbose_name="登记时间",
        help_text="登记时间",
        db_comment="登记时间"
    )

    # 登记人ID
    register_user_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        verbose_name="登记人ID",
        help_text="登记人ID",
        db_comment="登记人ID"
    )

    # 备注
    remark = models.TextField(
        null=True,
        blank=True,
        verbose_name="备注",
        help_text="备注信息",
        db_comment="备注信息"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "entry_reg"
        verbose_name = "进场登记"
        verbose_name_plural = verbose_name
        ordering = ["-create_datetime"]
        indexes = [
            models.Index(fields=["task_type"], name="idx_er_task_type"),
            models.Index(fields=["task_id"], name="idx_er_task_id"),
            models.Index(fields=["team_vehicle_id"], name="idx_er_team_vehicle_id"),
        ]

    def __str__(self):
        return f"进场登记-{self.task_type}-{self.task_id}"
