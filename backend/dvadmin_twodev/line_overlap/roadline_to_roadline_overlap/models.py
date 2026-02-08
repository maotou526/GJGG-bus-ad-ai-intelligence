'''
Description: 公交线路复线情况模型
Version: 1.0
Author: 王晨
Date: 2025-01-XX
LastEditors: 
LastEditTime: 
'''
from django.db import models
from django.utils import timezone
from django.db.models import Q
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.basedata.roadline_detail.models import RoadlineDetailModel
from dvadmin_twodev.basedata.roadline.models import RoadlineModel
from conf.env import CUS_TABLE_PREFIX


class RoadlineToRoadlineOverlapModel(BaseDataModel):
    """
    公交线路复线情况模型
    继承自BaseDataModel，自动获得所有通用字段
    专门用于存储两条公交线路走向之间的复线（重复段）关系
    
    复线说明：
    - 复线 = 两条公交线路走向之间的重复段
    - 段 = 轨迹集合
    - 轨迹格式：经度,纬度;经度,纬度（分号分隔点，逗号分隔经纬度）
    - 多段用 | 分割
    例如：120.123,31.456;120.124,31.457|120.125,31.458;120.126,31.459
    
    注意：线路走向可能会调整，调整后原来的线路就失效了（通过exec_day和expiry_day判断）
    """
    
    # 主线路外键
    main_roadline = models.ForeignKey(
        RoadlineModel,
        on_delete=models.CASCADE,
        db_constraint=False,  # 不创建数据库外键约束
        null=True,
        blank=True,
        verbose_name="主线路",
        help_text="主线路",
        related_name="main_roadline_overlaps"
    )
    
    # 主线路走向详情外键
    main_roadline_detail = models.ForeignKey(
        RoadlineDetailModel,
        on_delete=models.CASCADE,
        db_constraint=False,  # 不创建数据库外键约束
        null=True,
        blank=True,
        verbose_name="主线路走向详情",
        help_text="主线路的走向详情",
        related_name="main_roadline_detail_overlaps"
    )
    
    # 主线路编号（行业线路编号）
    main_roadline_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="主线路编号",
        help_text="主线路的行业线路编号"
    )
    
    # 主线路名称（冗余字段，方便查询）
    main_roadline_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="主线路名称",
        help_text="主线路名称"
    )
    
    # 主线路上下行：0上行，1下行
    main_roadline_updown = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="主线路上下行",
        help_text="主线路上下行：0上行，1下行"
    )
    
    # 副线路外键
    vice_roadline = models.ForeignKey(
        RoadlineModel,
        on_delete=models.CASCADE,
        db_constraint=False,  # 不创建数据库外键约束
        null=True,
        blank=True,
        verbose_name="副线路",
        help_text="副线路",
        related_name="vice_roadline_overlaps"
    )
    
    # 副线路走向详情外键
    vice_roadline_detail = models.ForeignKey(
        RoadlineDetailModel,
        on_delete=models.CASCADE,
        db_constraint=False,  # 不创建数据库外键约束
        null=True,
        blank=True,
        verbose_name="副线路走向详情",
        help_text="副线路的走向详情",
        related_name="vice_roadline_detail_overlaps"
    )
    
    # 副线路编号（行业线路编号）
    vice_roadline_code = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="副线路编号",
        help_text="副线路的行业线路编号"
    )
    
    # 副线路名称（冗余字段，方便查询）
    vice_roadline_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="副线路名称",
        help_text="副线路名称"
    )
    
    # 副线路上下行：0上行，1下行
    vice_roadline_updown = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="副线路上下行",
        help_text="副线路上下行：0上行，1下行"
    )
    
    # 复线长度（米）
    repeat_line_length = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="复线长度",
        help_text="复线长度（米）"
    )
    
    # 主线路复线率（复线长度/主线路长度）
    main_repeat_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="主线路复线率",
        help_text="复线率（复线长度/主线路长度）"
    )
    
    # 副线路复线率（复线长度/副线路长度）
    vice_repeat_rate = models.DecimalField(
        max_digits=12,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name="副线路复线率",
        help_text="复线率（复线长度/副线路长度）"
    )
    
    # 复线轨迹02坐标系
    # 格式：经度,纬度;经度,纬度|经度,纬度;经度,纬度（多段用|分割）
    repeat_lon_lat02 = models.TextField(
        null=True,
        blank=True,
        verbose_name="复线轨迹02坐标",
        help_text="GCJ02坐标系复线轨迹数据，格式：经度,纬度;经度,纬度|经度,纬度;经度,纬度（多段用|分割）"
    )
    
    # 复线轨迹84坐标系
    # 格式：经度,纬度;经度,纬度|经度,纬度;经度,纬度（多段用|分割）
    repeat_lon_lat84 = models.TextField(
        null=True,
        blank=True,
        verbose_name="复线轨迹84坐标",
        help_text="WGS84坐标系复线轨迹数据，格式：经度,纬度;经度,纬度|经度,纬度;经度,纬度（多段用|分割）"
    )
    
    # 启用日期
    exec_day = models.DateField(
        null=True,
        blank=True,
        verbose_name="启用日期",
        help_text="复线情况的启用日期，线路走向调整后原记录失效"
    )
    
    # 截止日期
    expiry_day = models.DateField(
        null=True,
        blank=True,
        verbose_name="截止日期",
        help_text="复线情况的截止日期，线路走向调整后原记录失效"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "roadline_to_roadline_overlap"
        verbose_name = "公交线路复线情况表"
        verbose_name_plural = verbose_name
        ordering = ['main_roadline_detail', '-exec_day', '-create_datetime']
        indexes = [
            models.Index(fields=['main_roadline'], name='idx_main_roadline'),
            models.Index(fields=['vice_roadline'], name='idx_vice_roadline'),
            models.Index(fields=['main_roadline_detail'], name='idx_main_roadline_detail'),
            models.Index(fields=['vice_roadline_detail'], name='idx_vice_roadline_detail'),
            models.Index(fields=['main_roadline_code'], name='idx_main_roadline_code'),
            models.Index(fields=['vice_roadline_code'], name='idx_vice_roadline_code'),
            models.Index(fields=['main_roadline_detail', 'vice_roadline_detail'], name='idx_main_vice'),
            models.Index(fields=['exec_day', 'expiry_day'], name='idx_exec_expiry'),
        ]
        # 唯一约束：同一对主副线路在同一时间段只能有一条复线记录
        unique_together = [['main_roadline_detail', 'vice_roadline_detail', 'exec_day']]
    
    def __str__(self):
        """字符串表示"""
        main_code = self.main_roadline_code or "未知"
        vice_code = self.vice_roadline_code or "未知"
        exec_date = self.exec_day.strftime('%Y-%m-%d') if self.exec_day else "未设置"
        return f"{main_code} <-> {vice_code} 复线 ({exec_date})"
    
    @property
    def is_valid(self):
        """
        判断当前复线记录是否有效（在当前日期范围内）
        """
        today = timezone.now().date()
        
        if self.exec_day is not None:
            if self.exec_day > today:
                return False
        
        if self.expiry_day is not None:
            if self.expiry_day < today:
                return False
        
        return True
    
    @property
    def segment_list_02(self):
        """
        获取02坐标系的段列表
        返回格式：[['经度,纬度', '经度,纬度'], ['经度,纬度', '经度,纬度']]
        """
        if not self.repeat_lon_lat02:
            return []
        
        segments = self.repeat_lon_lat02.split('|')
        return [segment.split(';') for segment in segments if segment.strip()]
    
    @classmethod
    def get_valid_overlaps(cls, date=None):
        """
        获取指定日期有效的复线记录
        
        Args:
            date: 查询日期，默认为今天
            
        Returns:
            QuerySet: 有效的复线记录查询集
        """
        if date is None:
            date = timezone.now().date()
        
        return cls.objects.filter(
            Q(exec_day__isnull=True) | Q(exec_day__lte=date),
            Q(expiry_day__isnull=True) | Q(expiry_day__gte=date)
        )
    
    def save(self, *args, **kwargs):
        """
        重写保存方法，自动更新冗余字段
        """
        # 如果主线路存在，自动填充主线路编号和名称
        if self.main_roadline:
            if not self.main_roadline_code:
                # 优先使用行业线路编号，如果没有则使用企业线路编码
                self.main_roadline_code = (
                    self.main_roadline.ygc_code or 
                    self.main_roadline.normal_code or 
                    None
                )
            if not self.main_roadline_name:
                self.main_roadline_name = self.main_roadline.line_name
        
        # 如果主线路详情存在，自动填充主线路编号、名称和上下行
        if self.main_roadline_detail:
            if self.main_roadline_detail.roadline:
                if not self.main_roadline_code:
                    # 优先使用行业线路编号，如果没有则使用企业线路编码
                    self.main_roadline_code = (
                        self.main_roadline_detail.roadline.ygc_code or 
                        self.main_roadline_detail.roadline.normal_code or 
                        None
                    )
                if not self.main_roadline_name:
                    self.main_roadline_name = self.main_roadline_detail.roadline.line_name
            if self.main_roadline_updown is None:
                self.main_roadline_updown = self.main_roadline_detail.up_down
            
            # 如果未设置启用日期，尝试从主线路详情获取
            if self.exec_day is None and self.main_roadline_detail.exec_day:
                self.exec_day = self.main_roadline_detail.exec_day
            
            # 如果未设置截止日期，尝试从主线路详情获取
            if self.expiry_day is None and self.main_roadline_detail.expiry_day:
                self.expiry_day = self.main_roadline_detail.expiry_day
        
        # 如果副线路存在，自动填充副线路编号和名称
        if self.vice_roadline:
            if not self.vice_roadline_code:
                # 优先使用行业线路编号，如果没有则使用企业线路编码
                self.vice_roadline_code = (
                    self.vice_roadline.ygc_code or 
                    self.vice_roadline.normal_code or 
                    None
                )
            if not self.vice_roadline_name:
                self.vice_roadline_name = self.vice_roadline.line_name
        
        # 如果副线路详情存在，自动填充副线路编号、名称和上下行
        if self.vice_roadline_detail:
            if self.vice_roadline_detail.roadline:
                if not self.vice_roadline_code:
                    # 优先使用行业线路编号，如果没有则使用企业线路编码
                    self.vice_roadline_code = (
                        self.vice_roadline_detail.roadline.ygc_code or 
                        self.vice_roadline_detail.roadline.normal_code or 
                        None
                    )
                if not self.vice_roadline_name:
                    self.vice_roadline_name = self.vice_roadline_detail.roadline.line_name
            if self.vice_roadline_updown is None:
                self.vice_roadline_updown = self.vice_roadline_detail.up_down
        
        # 自动计算复线率（如果复线长度和线路长度都存在）
        # 注意：repeat_line_length 单位是米，line_length 单位是公里，需要统一单位
        if self.repeat_line_length is not None:
            if self.main_roadline_detail and self.main_roadline_detail.line_length:
                main_length_km = float(self.main_roadline_detail.line_length)
                main_length_m = main_length_km * 1000  # 转换为米
                if main_length_m > 0:
                    self.main_repeat_rate = self.repeat_line_length / main_length_m
            
            if self.vice_roadline_detail and self.vice_roadline_detail.line_length:
                vice_length_km = float(self.vice_roadline_detail.line_length)
                vice_length_m = vice_length_km * 1000  # 转换为米
                if vice_length_m > 0:
                    self.vice_repeat_rate = self.repeat_line_length / vice_length_m
        
        super().save(*args, **kwargs)
