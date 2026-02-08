'''
Description: 公司模型
Version: 1.0
Autor: 王晨
Date: 2025-10-09 17:32:55
LastEditors: 王晨
LastEditTime: 2025-10-13 09:36:23
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from conf.env import CUS_TABLE_PREFIX

class CompanyModel(BaseDataModel):
    """
    公司模型
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 公司分类
    category = models.IntegerField(
        null=False,
        verbose_name="公司分类",
        help_text="公司分类"
    )
    
    # 上级公司ID
    parentid = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="上级公司ID",
        help_text="上级公司ID"
    )
    
    # 编码
    encode = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='encode',
        verbose_name="编码",
        help_text="编码"
    )
    
    # 简称
    shortname = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='shortname',
        verbose_name="简称",
        help_text="简称"
    )
    
    # 全称
    fullname = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='fullname',
        verbose_name="全称",
        help_text="全称"
    )
    
    # 公司性质
    nature = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='nature',
        verbose_name="公司性质",
        help_text="公司性质"
    )
    
    # 外线电话
    outerPhone = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='outerphone',
        verbose_name="外线电话",
        help_text="外线电话"
    )
    
    # 内线电话
    innerPhone = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='innerphone',
        verbose_name="内线电话",
        help_text="内线电话"
    )
    
    # 传真
    fax = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='fax',
        verbose_name="传真",
        help_text="传真"
    )
    
    # 邮政编码
    postalcode = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='postalcode',
        verbose_name="邮政编码",
        help_text="邮政编码"
    )
    
    # 邮箱
    email = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='email',
        verbose_name="邮箱",
        help_text="邮箱"
    )
    
    # 负责人
    manager = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='manager',
        verbose_name="负责人",
        help_text="负责人"
    )
    
    # 省份ID
    provinceId = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='provinceid',
        verbose_name="省份ID",
        help_text="省份ID"
    )
    
    # 城市ID
    cityId = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='cityid',
        verbose_name="城市ID",
        help_text="城市ID"
    )
    
    # 区县ID
    countyId = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='countyid',
        verbose_name="区县ID",
        help_text="区县ID"
    )
    
    # 详细地址
    address = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_column='address',
        verbose_name="详细地址",
        help_text="详细地址"
    )
    
    # 网址
    webAddress = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        db_column='webaddress',
        verbose_name="网址",
        help_text="网址"
    )
    
    # 成立时间
    foundedTime = models.DateTimeField(
        null=True,
        blank=True,
        db_column='foundedtime',
        verbose_name="成立时间",
        help_text="成立时间"
    )
    
    # 经营范围
    businessScope = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        db_column='businessscope',
        verbose_name="经营范围",
        help_text="经营范围"
    )
    
    # 排序码
    sortcode = models.IntegerField(
        null=False,
        db_column='sortcode',
        verbose_name="排序码",
        help_text="排序码"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "company"
        verbose_name = "公司表"
        verbose_name_plural = verbose_name
        ordering = ['sortcode', 'fullname']

