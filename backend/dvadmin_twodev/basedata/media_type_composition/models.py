'''
Description: 媒体类型组合关系模型
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from conf.env import CUS_TABLE_PREFIX
from dvadmin_twodev.basedata.media_type.models import AdMediaTypeModel


class AdMediaTypeCompositionModel(BaseDataModel):
    """
    媒体类型组合关系模型
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 组合类型ID
    composite_type_id = models.CharField(
        max_length=36,
        null=False,
        blank=False,
        db_column='composite_type_id',
        verbose_name="组合类型ID",
        help_text="关联AdMediaTypeModel (is_composite=True)",
        db_comment="组合类型ID，关联AdMediaTypeModel (is_composite=True)"
    )

    # 基础类型ID
    component_type_id = models.CharField(
        max_length=36,
        null=False,
        blank=False,
        db_column='component_type_id',
        verbose_name="基础类型ID",
        help_text="关联AdMediaTypeModel (is_composite=False)",
        db_comment="基础类型ID，关联AdMediaTypeModel (is_composite=False)"
    )

    # 显示顺序
    sort_order = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="显示顺序",
        help_text="组成部分的排序",
        db_comment="显示顺序，组成部分的排序"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "ad_media_type_composition"
        verbose_name = "媒体类型组合关系表"
        verbose_name_plural = verbose_name
        ordering = ['composite_type_id', 'sort_order']
        indexes = [
            models.Index(fields=['composite_type_id']),
            models.Index(fields=['component_type_id']),
            models.Index(fields=['composite_type_id', 'component_type_id']),
        ]
        # 唯一约束：同一个组合类型不能包含重复的基础类型
        unique_together = [['composite_type_id', 'component_type_id']]
