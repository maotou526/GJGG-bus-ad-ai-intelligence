'''
Description: 车辆广告资源位模型
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from dvadmin_twodev.basedata.vehicle.models import VehicleModel
from dvadmin_twodev.basedata.media_type.models import AdMediaTypeModel
from conf.env import CUS_TABLE_PREFIX


class VehicleAdResourceModel(BaseDataModel):
    """
    车辆广告资源位模型
    继承自BaseDataModel,自动获得所有通用字段
    包含:id(主键)、description(描述)、creator(创建人)、modifier(修改人)、
    dept_belong_id(数据归属部门)、create_datetime(创建时间)、update_datetime(修改时间)、
    delete_mark(删除标记)、enabled_mark(启用标记)、creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # 资源编码
    resource_code = models.CharField(
        max_length=64,
        null=False,
        blank=False,
        verbose_name="资源编码",
        help_text="唯一编码，如'V100-LEFT'（车辆100左侧）",
        db_comment="资源编码，唯一编码，如'V100-LEFT'（车辆100左侧）"
    )

    # 车辆ID
    vehicle_id = models.ForeignKey(
        VehicleModel,
        on_delete=models.CASCADE,
        db_column='vehicle_id',  # 明确指定数据库列名
        db_constraint=False,  # 不创建数据库外键约束
        null=False,
        blank=False,
        verbose_name="车辆ID",
        help_text="关联车辆表",
        db_comment="车辆ID，关联车辆表"
    )

    # 基础媒体类型ID
    base_media_type_id = models.ForeignKey(
        AdMediaTypeModel,
        on_delete=models.CASCADE,
        db_column='base_media_type_id',  # 明确指定数据库列名
        db_constraint=False,  # 不创建数据库外键约束
        null=False,
        blank=False,
        verbose_name="基础媒体类型ID",
        help_text="关联媒体类型表，必须是基础类型(is_composite=False)",
        db_comment="基础媒体类型ID，关联媒体类型表，必须是基础类型(is_composite=False)"
    )

    # 资源状态
    resource_status = models.IntegerField(
        null=False,
        blank=False,
        default=1,
        verbose_name="资源状态",
        help_text="资源状态：1=空闲, 2=预订, 3=在刊, 4=下刊, 5=维修中, 6=不可用, 7=到期未下刊",
        db_comment="资源状态：1=空闲, 2=预订, 3=在刊, 4=下刊, 5=维修中, 6=不可用, 7=到期未下刊"
    )

    # 当前订单ID
    current_order_id = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="当前订单ID",
        help_text="关联当前占用该资源的订单（如有）",
        db_comment="当前订单ID，关联当前占用该资源的订单（如有）"
    )

    # 投放开始日期（预订/计划）
    scheduled_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="投放开始日期",
        help_text="预订或计划的投放开始日期",
        db_comment="投放开始日期，预订或计划的投放开始日期"
    )

    # 投放结束日期（预订/计划）
    scheduled_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="投放结束日期",
        help_text="预订或计划的投放结束日期",
        db_comment="投放结束日期，预订或计划的投放结束日期"
    )

    # 上刊日期
    on_air_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="上刊日期",
        help_text="实际上刊（发布）日期",
        db_comment="上刊日期，实际上刊（发布）日期"
    )

    # 下刊日期
    off_air_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="下刊日期",
        help_text="实际下刊（撤除）日期",
        db_comment="下刊日期，实际下刊（撤除）日期"
    )

    # 备注
    remark = models.TextField(
        null=True,
        blank=True,
        verbose_name="备注",
        help_text="其他说明",
        db_comment="备注，其他说明"
    )

    def check_schedule_conflict(self, exclude_id=None):
        """
        检查排期冲突
        
        冲突规则：
        - vehicle_id 和 base_media_type_id 为一个最小单位
        - 相同 vehicle_id 和 base_media_type_id 的 scheduled_start_date 到 scheduled_end_date 的日期范围不能重叠
        
        参数:
            exclude_id: 排除的ID（用于更新时排除自身）
        
        返回:
            tuple: (是否有冲突, 冲突的资源位列表)
        """
        # 如果没有日期信息，不进行冲突检测
        if not self.scheduled_start_date or not self.scheduled_end_date:
            return False, []
        
        # 如果开始日期晚于结束日期，不进行冲突检测（这种情况会在序列化器中验证）
        if self.scheduled_start_date > self.scheduled_end_date:
            return False, []
        
        # 查询相同 vehicle_id 和 base_media_type_id 的其他资源位
        queryset = VehicleAdResourceModel.objects.filter(
            vehicle_id=self.vehicle_id,
            base_media_type_id=self.base_media_type_id,
            delete_mark=0,  # 只检查未删除的记录
            enabled_mark=1  # 只检查启用的记录
        )
        
        # 排除自身（用于更新时）
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        elif self.pk:
            queryset = queryset.exclude(id=self.pk)
        
        # 检查日期范围是否有重叠
        # 日期重叠的条件：两个日期段有交集
        # 即：not (end1 < start2 or start1 > end2)
        conflicts = []
        for resource in queryset:
            # 跳过没有日期信息的记录
            if not resource.scheduled_start_date or not resource.scheduled_end_date:
                continue
            
            # 检查日期范围是否重叠
            # 重叠条件：resource.scheduled_start_date <= self.scheduled_end_date and resource.scheduled_end_date >= self.scheduled_start_date
            if resource.scheduled_start_date <= self.scheduled_end_date and resource.scheduled_end_date >= self.scheduled_start_date:
                conflicts.append(resource)
        
        has_conflict = len(conflicts) > 0
        return has_conflict, conflicts

    class Meta:
        db_table = CUS_TABLE_PREFIX + "vehicle_ad_resource"
        verbose_name = "车辆广告资源位表"
        verbose_name_plural = verbose_name
        ordering = ['vehicle_id', 'base_media_type_id', 'scheduled_start_date']
        # 组合唯一索引：一辆车 + 一个基础媒体类型 + 投放开始日期 + 投放结束日期 = 唯一的资源位记录
        # 这样同一个资源位可以有多个不同时间段的排期
        unique_together = [['vehicle_id', 'base_media_type_id', 'scheduled_start_date', 'scheduled_end_date']]
        indexes = [
            models.Index(fields=['vehicle_id', 'base_media_type_id']),
            models.Index(fields=['resource_status']),
            models.Index(fields=['current_order_id']),
            models.Index(fields=['scheduled_start_date', 'scheduled_end_date']),
        ]
