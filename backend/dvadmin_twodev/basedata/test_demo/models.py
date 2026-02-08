'''
Description: 环域信息数据模型定义
Version: 1.0
Author: CursorAgent
Date: 2025-11-10 00:00:00
LastEditors: 王晨
LastEditTime: 2025-11-10 15:08:03
'''
from django.db import models


class DcBaseTorusinfoModel(models.Model):
    """
    环域信息模型
    对接已存在于达梦数据库中的环域信息表
    """

    # 主键（对应数据库中的 F_Id 字段）
    id = models.CharField(
        max_length=50,
        primary_key=True,
        db_column="F_Id",
        verbose_name="主键",
        help_text="主键ID",
        db_comment="主键"
    )

    # 说明（对应数据库中的 F_Explain 字段）
    explain = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        db_column="F_Explain",
        verbose_name="说明",
        help_text="说明信息",
        db_comment="说明"
    )

    # 环域（对应数据库中的 F_Torus 字段）
    torus = models.IntegerField(
        null=True,
        blank=True,
        db_column="F_Torus",
        verbose_name="环域",
        help_text="环域值",
        db_comment="环域"
    )

    # 备注（对应数据库中的 F_Remarks 字段）
    remarks = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        db_column="F_Remarks",
        verbose_name="备注",
        help_text="备注信息",
        db_comment="备注"
    )

    # 删除标识（对应数据库中的 F_DeleteMark 字段）
    delete_mark = models.IntegerField(
        null=True,
        blank=True,
        db_column="F_DeleteMark",
        verbose_name="删除标识",
        help_text="删除标识，0表示未删除，1表示已删除",
        db_comment="删除标识"
    )

    # 是否禁用（对应数据库中的 F_EnabledMark 字段）
    enabled_mark = models.IntegerField(
        null=True,
        blank=True,
        db_column="F_EnabledMark",
        verbose_name="是否禁用",
        help_text="是否禁用，0表示禁用，1表示启用",
        db_comment="是否禁用"
    )

    # 创建时间（对应数据库中的 F_CreateDate 字段）
    create_date = models.DateTimeField(
        null=True,
        blank=True,
        db_column="F_CreateDate",
        verbose_name="创建时间",
        help_text="创建时间",
        db_comment="创建时间"
    )

    # 创建用户ID（对应数据库中的 F_CreateUserId 字段）
    create_user_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column="F_CreateUserId",
        verbose_name="创建用户ID",
        help_text="创建用户ID",
        db_comment="创建用户ID"
    )

    # 创建用户名（对应数据库中的 F_CreateUserName 字段）
    create_user_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column="F_CreateUserName",
        verbose_name="创建用户名",
        help_text="创建用户名",
        db_comment="创建用户名"
    )

    # 修改时间（对应数据库中的 F_ModifyDate 字段）
    modify_date = models.DateTimeField(
        null=True,
        blank=True,
        db_column="F_ModifyDate",
        verbose_name="修改时间",
        help_text="修改时间",
        db_comment="修改时间"
    )

    # 修改用户ID（对应数据库中的 F_ModifyUserId 字段）
    modify_user_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column="F_ModifyUserId",
        verbose_name="修改用户ID",
        help_text="修改用户ID",
        db_comment="修改用户ID"
    )

    # 修改用户名（对应数据库中的 F_ModifyUserName 字段）
    modify_user_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column="F_ModifyUserName",
        verbose_name="修改用户名",
        help_text="修改用户名",
        db_comment="修改用户名"
    )

    class Meta:
        db_table = "dc_base_torusinfo"
        verbose_name = "环域信息"
        verbose_name_plural = "环域信息"
        managed = False

    def __str__(self):
        return f"环域信息-{self.id}"
