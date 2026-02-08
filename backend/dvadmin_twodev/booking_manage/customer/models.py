'''
Description: 客户模型
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.booking_manage.agent.models import AgentModel
from conf.env import CUS_TABLE_PREFIX


class CustomerModel(BaseDataModel):
    """
    客户模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 数据归属代理商（NULL=自营客户，有值=代理商客户）
    agent_id = models.ForeignKey(
        AgentModel,
        on_delete=models.SET_NULL,
        db_column='agent_id',
        db_constraint=False,
        null=True,
        blank=True,
        verbose_name="数据归属代理商",
        help_text="关联代理商表，NULL=自营客户，有值=代理商客户",
        db_comment="数据归属代理商，关联代理商表，NULL=自营客户，有值=代理商客户"
    )

    # 客户编码
    customer_code = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        verbose_name="客户编码",
        help_text="唯一编码，自动生成",
        db_comment="客户编码，唯一编码，自动生成"
    )

    # 公司名称
    company_name = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        verbose_name="公司名称",
        help_text="客户公司全称",
        db_comment="公司名称，客户公司全称"
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

    # 行业分类
    industry = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="行业分类",
        help_text="行业分类：1=快消, 2=金融, 3=地产, 4=互联网, 5=其他",
        db_comment="行业分类：1=快消, 2=金融, 3=地产, 4=互联网, 5=其他"
    )

    # 行业标签
    industry_tags = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="行业标签",
        help_text="如\"食品,饮料\"，逗号分隔",
        db_comment="行业标签，如\"食品,饮料\"，逗号分隔"
    )

    # 联系人姓名
    contact_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="联系人姓名",
        help_text="主要联系人",
        db_comment="联系人姓名，主要联系人"
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

    # 公司地址
    company_address = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="公司地址",
        help_text="详细地址",
        db_comment="公司地址，详细地址"
    )

    # 客户等级
    customer_level = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="客户等级",
        help_text="客户等级：1=重点客户, 2=普通客户, 3=潜在客户",
        db_comment="客户等级：1=重点客户, 2=普通客户, 3=潜在客户"
    )

    # 首次合作时间
    first_cooperation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="首次合作时间",
        help_text="第一次签订单的时间",
        db_comment="首次合作时间，第一次签订单的时间"
    )

    # 最近合作时间
    last_cooperation_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="最近合作时间",
        help_text="最近一次签订单的时间",
        db_comment="最近合作时间，最近一次签订单的时间"
    )

    # 累计合作金额
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="累计合作金额",
        help_text="历史累计金额（元）",
        db_comment="累计合作金额，历史累计金额（元）"
    )

    # 累计合作次数
    cooperation_count = models.IntegerField(
        null=True,
        blank=True,
        default=0,
        verbose_name="累计合作次数",
        help_text="历史订单数量",
        db_comment="累计合作次数，历史订单数量"
    )

    # 状态
    status = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        verbose_name="状态",
        help_text="状态：1=活跃, 2=休眠, 3=流失",
        db_comment="状态：1=活跃, 2=休眠, 3=流失"
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
        db_table = CUS_TABLE_PREFIX + "customer"
        verbose_name = "客户表"
        verbose_name_plural = verbose_name
        ordering = ['company_name']
        indexes = [
            models.Index(fields=['customer_code']),
            models.Index(fields=['agent_id']),
            models.Index(fields=['industry']),
            models.Index(fields=['customer_level']),
            models.Index(fields=['status']),
        ]
