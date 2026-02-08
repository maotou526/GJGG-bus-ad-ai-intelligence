'''
Description: 代理商模型
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from conf.env import CUS_TABLE_PREFIX


class AgentModel(BaseDataModel):
    """
    代理商模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 代理商编码
    agent_code = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        verbose_name="代理商编码",
        help_text="唯一编码，自动生成",
        db_comment="代理商编码，唯一编码，自动生成"
    )

    # 公司名称
    company_name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        verbose_name="公司名称",
        help_text="代理商公司全称",
        db_comment="公司名称，代理商公司全称"
    )

    # 统一社会信用代码
    credit_code = models.CharField(
        max_length=18,
        null=True,
        blank=True,
        verbose_name="统一社会信用代码",
        help_text="营业执照号",
        db_comment="统一社会信用代码，营业执照号"
    )

    # 法定代表人
    legal_person = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="法定代表人",
        help_text="法人姓名",
        db_comment="法定代表人，法人姓名"
    )

    # 注册资本
    registered_capital = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="注册资本",
        help_text="单位：万元",
        db_comment="注册资本，单位：万元"
    )

    # 成立日期
    established_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="成立日期",
        help_text="公司成立时间",
        db_comment="成立日期，公司成立时间"
    )

    # 公司地址
    company_address = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="公司地址",
        help_text="详细地址",
        db_comment="公司地址，详细地址"
    )

    # 联系电话
    contact_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name="联系电话",
        help_text="主要联系电话",
        db_comment="联系电话，主要联系电话"
    )

    # 联系邮箱
    contact_email = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="联系邮箱",
        help_text="主要联系邮箱",
        db_comment="联系邮箱，主要联系邮箱"
    )

    # 合作等级
    cooperation_level = models.IntegerField(
        null=False,
        blank=False,
        default=3,
        verbose_name="合作等级",
        help_text="合作等级：1=A级, 2=B级, 3=C级",
        db_comment="合作等级：1=A级, 2=B级, 3=C级"
    )

    # 合同开始日期
    contract_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="合同开始日期",
        help_text="合作合同起始日期",
        db_comment="合同开始日期，合作合同起始日期"
    )

    # 合同结束日期
    contract_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="合同结束日期",
        help_text="合作合同结束日期",
        db_comment="合同结束日期，合作合同结束日期"
    )

    # 结算方式
    settlement_type = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="结算方式",
        help_text="结算方式：1=月结, 2=季结, 3=年结",
        db_comment="结算方式：1=月结, 2=季结, 3=年结"
    )

    # 开户银行
    bank_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="开户银行",
        help_text="结算银行名称",
        db_comment="开户银行，结算银行名称"
    )

    # 银行账号
    bank_account = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="银行账号",
        help_text="结算账号",
        db_comment="银行账号，结算账号"
    )

    # 业务负责人
    business_manager = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="业务负责人",
        help_text="广告公司侧对接人",
        db_comment="业务负责人，广告公司侧对接人"
    )

    # 备注
    remark = models.TextField(
        null=True,
        blank=True,
        verbose_name="备注",
        help_text="其他说明",
        db_comment="备注，其他说明"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "agent"
        verbose_name = "代理商表"
        verbose_name_plural = verbose_name
        ordering = ['company_name']
        indexes = [
            models.Index(fields=['agent_code']),
            models.Index(fields=['cooperation_level']),
            models.Index(fields=['contract_start_date', 'contract_end_date']),
        ]
