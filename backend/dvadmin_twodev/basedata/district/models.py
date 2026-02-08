'''
Description: 区属模型
Version: 1.0
Autor: AI Assistant
Date: 2025-10-16
LastEditors: 
LastEditTime: 2025-10-16
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from conf.env import CUS_TABLE_PREFIX


class DistrictModel(BaseDataModel):
    """
    区属模型
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """


    # 区属名称
    name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="区属名称",
        help_text="区属名称"
    )

    # 区属类型(市/区/街道)
    type = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="区属类型",
        help_text="区属类型(市/区/街道)"
    )

    # 父级区属
    parent_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        db_index=True,
        verbose_name="父级区属ID",
        help_text="父级区属GUID"
    )

    # 停车场围栏坐标串
    fence = models.TextField(
        null=True,
        blank=True,
        verbose_name="围栏坐标",
        help_text="停车场围栏坐标串，格式：经度1,纬度1;经度2,纬度2"
    )

    # 中心点坐标
    center_coord = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="中心点坐标",
        help_text="中心点坐标，格式：经度,纬度"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "district"
        verbose_name = "区属表"
        verbose_name_plural = verbose_name
        ordering = ['name']
        indexes = [
            models.Index(fields=['parent_id']),
            models.Index(fields=['type']),
        ]
