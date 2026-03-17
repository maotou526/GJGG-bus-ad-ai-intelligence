'''
Description: 施工团队车辆模型
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


class ConstructionTeamVehicleModel(BaseDataModel):
    """
    施工团队车辆模型
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
        related_name="vehicles",
    )

    # 车辆编号
    vehicle_no = models.CharField(
        max_length=50,
        null=False,
        blank=False,
        verbose_name="车辆编号",
        help_text="车辆编号",
        db_comment="车辆编号"
    )

    # 车牌号
    plate_no = models.CharField(
        max_length=20,
        null=False,
        blank=False,
        unique=True,
        verbose_name="车牌号",
        help_text="车牌号，唯一",
        db_comment="车牌号，唯一"
    )

    # 车辆类型
    vehicle_type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="车辆类型",
        help_text="车辆类型",
        db_comment="车辆类型"
    )

    # 负责人ID
    leader_id = models.CharField(
        max_length=36,
        null=False,
        blank=False,
        verbose_name="负责人ID",
        help_text="关联ConstructionTeamMemberModel",
        db_comment="负责人ID，关联施工团队成员表"
    )

    # 负责人姓名
    leader_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="负责人姓名",
        help_text="负责人姓名，冗余字段",
        db_comment="负责人姓名，冗余字段"
    )

    # 负责人电话
    leader_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="负责人电话",
        help_text="负责人电话，冗余字段",
        db_comment="负责人电话，冗余字段"
    )

    # 车辆状态
    vehicle_status = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        verbose_name="车辆状态",
        help_text="车辆状态：1=正常, 2=维修中, 3=停用",
        db_comment="车辆状态：1=正常, 2=维修中, 3=停用"
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
        db_table = CUS_TABLE_PREFIX + "construction_team_vehicle"
        verbose_name = "施工团队车辆表"
        verbose_name_plural = verbose_name
        ordering = ["-create_datetime"]
        indexes = [
            models.Index(fields=["team_id"]),
            models.Index(fields=["plate_no"]),
            models.Index(fields=["vehicle_status"]),
        ]
