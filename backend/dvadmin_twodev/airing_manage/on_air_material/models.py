'''
Description: 上刊材料模型
Version: 1.0
Autor: AI Assistant
Date: 2026-03-17
LastEditors:
LastEditTime: 2026-03-17
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.airing_manage.on_air_order.models import OnAirOrderModel
from conf.env import CUS_TABLE_PREFIX


class OnAirMaterialModel(BaseDataModel):
    """
    上刊材料模型
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
        null=False,
        blank=False,
        verbose_name="上刊订单ID",
        help_text="关联上刊订单表（dwd_on_air_order）",
        db_comment="上刊订单ID，关联上刊订单表（dwd_on_air_order）",
        related_name="materials",
    )

    # 材料类别
    material_category = models.IntegerField(
        null=False,
        blank=False,
        verbose_name="材料类别",
        help_text="材料类别：1=广告画面, 2=合规证明, 3=施工方案, 4=其他",
        db_comment="材料类别：1=广告画面, 2=合规证明, 3=施工方案, 4=其他"
    )

    # 材料类型编码
    material_type_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="材料类型编码",
        help_text="材料类型编码",
        db_comment="材料类型编码"
    )

    # 材料类型名称
    material_type_name = models.CharField(
        max_length=100,
        null=False,
        blank=False,
        verbose_name="材料类型名称",
        help_text="材料类型名称",
        db_comment="材料类型名称"
    )

    # 文件名
    file_name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        verbose_name="文件名",
        help_text="文件名",
        db_comment="文件名"
    )

    # 文件路径
    file_path = models.CharField(
        max_length=500,
        null=False,
        blank=False,
        verbose_name="文件路径",
        help_text="文件路径",
        db_comment="文件路径"
    )

    # 文件大小（字节）
    file_size = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="文件大小",
        help_text="文件大小，单位：字节",
        db_comment="文件大小，单位：字节"
    )

    # 文件格式
    file_format = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="文件格式",
        help_text="文件格式，如：jpg, png, pdf",
        db_comment="文件格式，如：jpg, png, pdf"
    )

    # 是否必需
    is_required = models.BooleanField(
        default=False,
        verbose_name="是否必需",
        help_text="是否必需材料",
        db_comment="是否必需材料"
    )

    # 审核状态
    audit_status = models.IntegerField(
        null=True,
        blank=True,
        default=10,
        verbose_name="审核状态",
        help_text="审核状态：10=待AI审核, 11=AI审核中, 20=待人工复核, 30=已通过, 40=已驳回",
        db_comment="审核状态：10=待AI审核, 11=AI审核中, 20=待人工复核, 30=已通过, 40=已驳回"
    )

    # 最近AI审核ID
    latest_ai_audit_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        verbose_name="最近AI审核ID",
        help_text="最近一次AI审核记录的ID",
        db_comment="最近一次AI审核记录的ID"
    )

    # 上传人ID
    uploader_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        verbose_name="上传人ID",
        help_text="上传人ID",
        db_comment="上传人ID"
    )

    # 上传时间
    upload_time = models.DateTimeField(
        null=False,
        blank=False,
        verbose_name="上传时间",
        help_text="上传时间",
        db_comment="上传时间"
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
        db_table = CUS_TABLE_PREFIX + "on_air_material"
        verbose_name = "上刊材料表"
        verbose_name_plural = verbose_name
        ordering = ["-create_datetime"]
        indexes = [
            models.Index(fields=["order_id"]),
            models.Index(fields=["material_category"]),
            models.Index(fields=["audit_status"]),
        ]
