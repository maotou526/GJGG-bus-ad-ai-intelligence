"""
Description: 上刊施工文件模型
Version: 1.0
"""
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.airing_manage.on_air_order_detail.models import OnAirOrderDetailModel
from conf.env import CUS_TABLE_PREFIX


class OnAirFileModel(BaseDataModel):
    """
    上刊施工文件模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 上刊订单明细ID
    order_detail_id = models.ForeignKey(
        OnAirOrderDetailModel,
        on_delete=models.PROTECT,
        db_column="order_detail_id",
        db_constraint=False,
        related_name="files",
        verbose_name="上刊订单明细ID",
        help_text="关联上刊订单明细",
        db_comment="上刊订单明细ID，关联上刊订单明细表"
    )

    # 文件类型
    file_type = models.IntegerField(
        verbose_name="文件类型",
        help_text="1:施工前, 2:施工中, 3:完工后",
        db_comment="文件类型：1=施工前, 2=施工中, 3=完工后"
    )

    # 文件路径
    file_path = models.CharField(
        max_length=500,
        verbose_name="文件路径",
        help_text="文件存储路径",
        db_comment="文件存储路径"
    )

    # 拍摄时间
    capture_time = models.DateTimeField(
        verbose_name="拍摄时间",
        help_text="拍摄时间",
        db_comment="拍摄时间"
    )

    # GPS位置
    gps_location = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="GPS位置",
        help_text="GPS位置信息",
        db_comment="GPS位置信息"
    )

    # 实际拍照的施工人员ID
    constructor_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        verbose_name="施工人员ID",
        help_text="实际拍照的施工人员",
        db_comment="实际拍照的施工人员ID"
    )

    # 上传人ID
    uploader_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        verbose_name="上传人ID",
        help_text="上传人",
        db_comment="上传人ID"
    )

    # 上传时间
    upload_time = models.DateTimeField(
        verbose_name="上传时间",
        help_text="上传时间",
        db_comment="上传时间"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "on_air_file"
        verbose_name = "上刊施工文件"
        verbose_name_plural = verbose_name
        ordering = ["-create_datetime"]
        indexes = [
            models.Index(fields=["order_detail_id"], name="idx_oaf_order_detail_id"),
            models.Index(fields=["file_type"], name="idx_oaf_file_type"),
        ]

    def __str__(self):
        return f"{self.file_path} - 类型{self.file_type}"
