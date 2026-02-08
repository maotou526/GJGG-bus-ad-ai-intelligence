'''
Description: 媒体类型模型
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from conf.env import CUS_TABLE_PREFIX


class AdMediaTypeModel(BaseDataModel):
    """
    媒体类型模型
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 类型名称
    media_name = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        verbose_name="类型名称",
        help_text="类型名称，如 '全车身', '大三侧', '车头', '普通灯箱'",
        db_comment="类型名称"
    )

    # 大类归属
    media_category = models.IntegerField(
        null=False,
        blank=False,
        verbose_name="大类归属",
        help_text="大类归属：1=车身广告, 2=站点广告",
        db_comment="大类归属：1=车身广告, 2=站点广告"
    )

    # 是否组合类型
    is_composite = models.BooleanField(
        null=False,
        blank=False,
        default=False,
        verbose_name="是否组合类型",
        help_text="是否组合类型：True=组合类型, False=基础类型",
        db_comment="是否组合类型：True=组合类型, False=基础类型"
    )

    # 规格参数
    spec_config = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="规格参数",
        help_text="描述尺寸、分辨率等，如 {'w':1200, 'h':800}",
        db_comment="规格参数，JSON格式，描述尺寸、分辨率等"
    )

    # 制作要求
    fabrication_req = models.TextField(
        null=True,
        blank=True,
        verbose_name="制作要求",
        help_text="材质、工艺要求描述",
        db_comment="制作要求，材质、工艺要求描述"
    )

    # 刊例价基准
    base_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="刊例价基准",
        help_text="该类型的标准基础价格",
        db_comment="刊例价基准，该类型的标准基础价格"
    )

    # 显示顺序
    sort_order = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="显示顺序",
        help_text="用于前端显示排序",
        db_comment="显示顺序，用于前端显示排序"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "ad_media_type"
        verbose_name = "媒体类型表"
        verbose_name_plural = verbose_name
        ordering = ['sort_order', 'media_name']
