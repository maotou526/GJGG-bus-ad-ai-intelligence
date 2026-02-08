"""
AI审核记录模型
Description: AI审核记录表，记录每次AI审核的完整结果
Version: 1.0
Date: 2026-02-03
"""
import uuid
from django.db import models
from django.utils import timezone
from dvadmin_twodev.baseentity.models import BaseDataModel
from conf.env import CUS_TABLE_PREFIX
from ..utils.audit_enums import (
    AuditSource, AuditType, AIConclusion, RiskLevel,
    AUDIT_SOURCE_CHOICES, AUDIT_TYPE_CHOICES, AI_CONCLUSION_CHOICES, RISK_LEVEL_CHOICES
)
from ..constants import PLATFORM_ALIBABA_BAILIAN
from ..utils.audit_helpers import generate_audit_no, calculate_duration, determine_need_manual_review


class AIAuditLogModel(BaseDataModel):
    """
    AI审核记录模型

    功能说明：
    - 记录每次AI审核的完整结果
    - 包括检测项、违规内容、风险点定位等
    - 支持关联订单审核和独立审核两种场景
    - 所有审核记录永久保留，不可删除

    继承自BaseDataModel，自动获得所有通用字段：
    - id(主键)、description(描述)、creator(创建人)、modifier(修改人)
    - dept_belong_id(数据归属部门)、company_belong_id(数据归属公司)
    - agent_id(数据归属代理商)、create_datetime(创建时间)、update_datetime(修改时间)
    - delete_mark(删除标记)、enabled_mark(启用标记)
    - creator_name(创建人姓名)、modifier_name(修改人姓名)

    文件关联说明：
    - 附件先上传到 dvadmin_system_file_list 表（通过 /api/system/file/ 接口）
    - 获得 file_id 后，再创建审核记录并关联
    - file_name、file_path 为冗余字段，便于查询
    """

    # 关联附件表
    file_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="附件ID",
        help_text="关联 dvadmin_system_file_list 表的 id",
        db_comment="关联附件ID，外键到 dvadmin_system_file_list"
    )

    # 审核编号
    audit_no = models.CharField(
        max_length=64,
        unique=True,
        verbose_name="审核编号",
        help_text="唯一编号，格式：AUD-YYYYMMDD-XXXX",
        db_comment="审核编号，格式：AUD-YYYYMMDD-XXXX"
    )

    # 审核来源
    audit_source = models.IntegerField(
        choices=[(k, v) for k, v in AUDIT_SOURCE_CHOICES.items()],
        verbose_name="审核来源",
        help_text="1:关联订单审核, 2:独立审核",
        db_comment="审核来源：1=关联订单审核, 2=独立审核"
    )

    # 关联材料ID（仅关联订单审核时有值）
    material_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="关联材料ID",
        help_text="关联 OnAirMaterialModel，仅关联订单审核时有值",
        db_comment="关联材料ID，关联 OnAirMaterialModel"
    )

    # 上刊订单ID（冗余字段，仅关联订单审核时有值）
    order_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
        verbose_name="上刊订单ID",
        help_text="冗余字段，关联 OnAirOrderModel，仅关联订单审核时有值",
        db_comment="上刊订单ID，冗余字段"
    )

    # 文件名称
    file_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        verbose_name="文件名称",
        help_text="原始文件名",
        db_comment="原始文件名"
    )

    # 文件路径
    file_path = models.CharField(
        max_length=500,
        verbose_name="文件路径",
        help_text="被审核的文件路径",
        db_comment="被审核的文件路径"
    )

    # 审核类型
    audit_type = models.IntegerField(
        choices=[(k, v) for k, v in AUDIT_TYPE_CHOICES.items()],
        verbose_name="审核类型",
        help_text="1:画面内容审核, 2:证明文件审核, 3:综合审核",
        db_comment="审核类型：1=画面内容审核, 2=证明文件审核, 3=综合审核"
    )

    # 调用平台
    platform = models.CharField(
        max_length=50,
        default=PLATFORM_ALIBABA_BAILIAN,
        verbose_name="调用平台",
        help_text="固定值：阿里百炼 或 Alibaba Bailian",
        db_comment="调用平台"
    )

    # 智能体ID（避免与通用字段agent_id冲突）
    agent_id_ext = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="智能体ID",
        help_text="阿里百炼的智能体ID（避免与通用字段agent_id冲突）",
        db_comment="阿里百炼的智能体ID"
    )

    # 请求时间
    request_time = models.DateTimeField(
        verbose_name="请求时间",
        help_text="发起审核请求的时间",
        db_comment="发起审核请求的时间"
    )

    # 响应时间
    response_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="响应时间",
        help_text="收到审核结果的时间",
        db_comment="收到审核结果的时间"
    )

    # 耗时(秒)
    duration_seconds = models.IntegerField(
        null=True,
        blank=True,
        verbose_name="耗时(秒)",
        help_text="审核耗时，自动计算",
        db_comment="审核耗时（秒）"
    )

    # AI判定结果
    ai_conclusion = models.IntegerField(
        choices=[(k, v) for k, v in AI_CONCLUSION_CHOICES.items()],
        verbose_name="AI判定结果",
        help_text="1:通过, 2:疑似违规, 3:明确违规, 4:审核失败",
        db_comment="AI判定结果：1=通过, 2=疑似违规, 3=明确违规, 4=审核失败"
    )

    # 综合风险等级
    risk_level = models.IntegerField(
        choices=[(k, v) for k, v in RISK_LEVEL_CHOICES.items()],
        null=True,
        blank=True,
        verbose_name="综合风险等级",
        help_text="1:无风险, 2:低风险, 3:中风险, 4:高风险",
        db_comment="综合风险等级：1=无风险, 2=低风险, 3=中风险, 4=高风险"
    )

    # 综合置信度
    confidence_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="综合置信度",
        help_text="0-100，AI判定的置信度",
        db_comment="综合置信度（0-100）"
    )

    # 检测项详情（JSON字段）
    detection_details = models.JSONField(
        null=True,
        blank=True,
        verbose_name="检测项详情",
        help_text="详细检测项列表（JSON格式）",
        db_comment="检测项详情（JSON）"
    )

    # 违规内容（JSON字段）
    violation_content = models.JSONField(
        null=True,
        blank=True,
        verbose_name="违规内容",
        help_text="检测到的违规内容列表（JSON格式）",
        db_comment="违规内容（JSON）"
    )

    # AI审核总结
    summary = models.TextField(
        null=True,
        blank=True,
        verbose_name="审核总结",
        help_text="AI对审核结果的综合总结说明",
        db_comment="AI审核总结"
    )

    # 原始响应
    raw_response = models.TextField(
        null=True,
        blank=True,
        verbose_name="原始响应",
        help_text="阿里百炼API的原始返回JSON（完整保存用于调试）",
        db_comment="API原始响应"
    )

    # 错误信息
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name="错误信息",
        help_text="如果审核失败，记录错误原因",
        db_comment="审核失败时的错误信息"
    )

    # 是否需人工复核
    need_manual_review = models.BooleanField(
        default=False,
        verbose_name="是否需人工复核",
        help_text="True=需要人工介入, False=可自动通过",
        db_comment="是否需要人工复核"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "ai_audit_log"
        verbose_name = "AI审核记录"
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
        indexes = [
            models.Index(fields=['audit_no'], name='idx_audit_no'),
            models.Index(fields=['material_id'], name='idx_material_id'),
            models.Index(fields=['order_id'], name='idx_order_id'),
            models.Index(fields=['audit_source'], name='idx_audit_source'),
            models.Index(fields=['ai_conclusion'], name='idx_ai_conclusion'),
            models.Index(fields=['create_datetime'], name='idx_create_time'),
        ]

    def save(self, *args, **kwargs):
        """重写save方法，自动生成ID、审核编号和计算耗时"""
        # 如果没有ID，自动生成UUID
        if not self.id:
            self.id = str(uuid.uuid4())

        # 如果没有审核编号，自动生成
        if not self.audit_no:
            self.audit_no = generate_audit_no()

        # 如果没有请求时间，设置为当前时间
        if not self.request_time:
            self.request_time = timezone.now()

        # 自动计算耗时
        if self.request_time and self.response_time:
            self.duration_seconds = calculate_duration(self.request_time, self.response_time)

        # 自动判断是否需要人工复核
        self.need_manual_review = determine_need_manual_review(
            self.ai_conclusion,
            self.risk_level,
            float(self.confidence_score) if self.confidence_score else None
        )

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.audit_no} - {self.get_ai_conclusion_display()}"
