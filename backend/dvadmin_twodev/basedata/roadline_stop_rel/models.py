
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.basedata.roadline.models import RoadlineModel
from dvadmin_twodev.basedata.roadline_detail.models import RoadlineDetailModel
from conf.env import CUS_TABLE_PREFIX

class RoadlineStopRelModel(BaseDataModel):
    """
    站点关联模型
    继承自BaseDataModel，自动获得所有通用字段
    包含：id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 线路主表外键
    roadline_id = models.ForeignKey(
        RoadlineModel,
        on_delete=models.CASCADE,
        db_column='roadline_id',
        db_constraint=False,  # 不创建数据库外键约束
        null=True,
        blank=True,
        verbose_name="关联线路",
        help_text="关联的线路主表",
        related_name="stop_relations"
    )
    
    # 线路详情表外键
    line_dtl_id = models.ForeignKey(
        RoadlineDetailModel,
        on_delete=models.CASCADE,
        db_column='line_dtl_id',
        db_constraint=False,  # 不创建数据库外键约束
        null=True,
        blank=True,
        verbose_name="关联线路详情",
        help_text="关联的线路详情表",
        related_name="stop_relations"
    )
    
    # 站序
    level_id = models.IntegerField(
        db_column='level_id',
        null=True,
        blank=True,
        verbose_name="站序",
        help_text="站点在线路中的序号"
    )
    
    # 站级名称
    level_name = models.CharField(
        max_length=100,
        db_column='level_name',
        null=True,
        blank=True,
        verbose_name="站级名称",
        help_text="站点级别名称"
    )
    
    # 站点ID
    stop_id = models.CharField(
        max_length=50,
        db_column='stop_id',
        null=True,
        blank=True,
        verbose_name="站点ID",
        help_text="站点ID，关联站点表的主键ID"
    )
    
    # 站点编号
    stop_code = models.CharField(
        max_length=50,
        db_column='stop_code',
        null=True,
        blank=True,
        verbose_name="站点编号",
        help_text="站点编号"
    )
    
    # 区属
    zone = models.CharField(
        max_length=100,
        db_column='zone',
        null=True,
        blank=True,
        verbose_name="区属",
        help_text="所属区域"
    )
    
    # 经度02
    lon02 = models.DecimalField(
        max_digits=20,
        decimal_places=16,
        db_column='lon02',
        null=True,
        blank=True,
        verbose_name="经度02",
        help_text="GCJ02坐标系经度"
    )
    
    # 纬度02
    lat02 = models.DecimalField(
        max_digits=20,
        decimal_places=16,
        db_column='lat02',
        null=True,
        blank=True,
        verbose_name="纬度02",
        help_text="GCJ02坐标系纬度"
    )
    
    # 经度84
    lon84 = models.DecimalField(
        max_digits=20,
        decimal_places=16,
        db_column='lon84',
        null=True,
        blank=True,
        verbose_name="经度84",
        help_text="WGS84坐标系经度"
    )
    
    # 纬度84
    lat84 = models.DecimalField(
        max_digits=20,
        decimal_places=16,
        db_column='lat84',
        null=True,
        blank=True,
        verbose_name="纬度84",
        help_text="WGS84坐标系纬度"
    )
    
    # 距上一站的距离
    to_next_metre = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        db_column='to_next_metre',
        null=True,
        blank=True,
        verbose_name="距上一站距离",
        help_text="距上一站的距离（米）"
    )
    
    # 网格转换经度02
    trans_lon02 = models.DecimalField(
        max_digits=20,
        decimal_places=16,
        db_column='trans_lon02',
        null=True,
        blank=True,
        verbose_name="网格转换经度02",
        help_text="网格转换后的经度坐标"
    )
    
    # 网格转换纬度02
    trans_lat02 = models.DecimalField(
        max_digits=20,
        decimal_places=16,
        db_column='trans_lat02',
        null=True,
        blank=True,
        verbose_name="网格转换纬度02",
        help_text="网格转换后的纬度坐标"
    )
    
    # 网格转换经度84
    trans_lon84 = models.DecimalField(
        max_digits=20,
        decimal_places=16,
        db_column='trans_lon84',
        null=True,
        blank=True,
        verbose_name="网格转换经度84",
        help_text="网格转换后的WGS84坐标系经度"
    )
    
    # 网格转换纬度84
    trans_lat84 = models.DecimalField(
        max_digits=20,
        decimal_places=16,
        db_column='trans_lat84',
        null=True,
        blank=True,
        verbose_name="网格转换纬度84",
        help_text="网格转换后的WGS84坐标系纬度"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "roadline_stop_rel"
        verbose_name = "站点关联表"
        verbose_name_plural = verbose_name
        ordering = ['roadline_id', 'line_dtl_id', 'level_id']