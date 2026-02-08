"""
AI审核反馈模型
Description: AI审核反馈表，记录人工审核员对AI审核结果的反馈
Version: 1.0
Date: 2026-02-03
"""
from django.db import models
from dvadmin_twodev.baseentity.models import BaseDataModel
from conf.env import CUS_TABLE_PREFIX
from ..utils.audit_enums import (
    ManualConclusion, FinalResult, AIAccuracy,
    MANUAL_CONCLUSION_CHOICES, FINAL_RESULT_CHOICES, AI_ACCURACY_CHOICES
)


class AIAuditFeedbackModel(BaseDataModel):
    """
    AI审核反馈模型

    功能说明：
    - 记录人工审核员对AI审核结果的反馈
    - 用于AI模型持续学习优化
    - 每个AI审核记录最多一条反馈记录

    继承自BaseDataModel，自动获得所有通用字段：
    - id(主键)、description(描述)、creator(创建人)、modifier(修改人)
    - dept_belong_id(数据归属部门)、company_belong_id(数据归属公司)
    - agent_id(数据归属代理商)、create_datetime(创建时间)、update_datetime(修改时间)
    - delete_mark(删除标记)、enabled_mark(启用标记)
    - creator_name(创建人姓名)、modifier_name(修改人姓名)
    """

    # AI审核记录ID（外键关联）
    audit_log_id = models.BigIntegerField(
        unique=True,  # 每个审核记录最多一条反馈
        verbose_name="AI审核记录ID",
        help_text="关联 AIAuditLogModel",
        db_comment="关联 AIAuditLogModel ID"
    )

    # 审核员ID（外键关联User表）
    reviewer_id = models.BigIntegerField(
        verbose_name="审核员ID",
        help_text="人工审核员（关联 User 表）",
        db_comment="审核员ID，关联 User 表"
    )

    # 审核员姓名（冗余字段）
    reviewer_name = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="审核员姓名",
        help_text="冗余字段",
        db_comment="审核员姓名（冗余）"
    )

    # 人工判定结果
    manual_conclusion = models.IntegerField(
        choices=[(k, v) for k, v in MANUAL_CONCLUSION_CHOICES.items()],
        verbose_name="人工判定结果",
        help_text="1:同意AI判定, 2:部分同意, 3:完全不同意",
        db_comment="人工判定结果：1=同意AI判定, 2=部分同意, 3=完全不同意"
    )

    # 最终审核结果
    final_result = models.IntegerField(
        choices=[(k, v) for k, v in FINAL_RESULT_CHOICES.items()],
        verbose_name="最终审核结果",
        help_text="1:通过, 2:驳回修改, 3:转法务审核",
        db_comment="最终审核结果：1=通过, 2=驳回修改, 3=转法务审核"
    )

    # AI判定准确性
    ai_accuracy = models.IntegerField(
        choices=[(k, v) for k, v in AI_ACCURACY_CHOICES.items()],
        null=True,
        blank=True,
        verbose_name="AI判定准确性",
        help_text="1:非常准确, 2:基本准确, 3:不太准确, 4:完全错误",
        db_comment="AI判定准确性：1=非常准确, 2=基本准确, 3=不太准确, 4=完全错误"
    )

    # 误判项（JSON字段）
    false_detections = models.JSONField(
        null=True,
        blank=True,
        verbose_name="误判项",
        help_text="AI误报的检测项列表（JSON格式）",
        db_comment="误判项（JSON）"
    )

    # 漏检项（JSON字段）
    missed_detections = models.JSONField(
        null=True,
        blank=True,
        verbose_name="漏检项",
        help_text="AI未检测到的违规项（JSON格式）",
        db_comment="漏检项（JSON）"
    )

    # 反馈说明
    feedback_text = models.TextField(
        null=True,
        blank=True,
        verbose_name="反馈说明",
        help_text="审核员的详细反馈意见",
        db_comment="审核员的详细反馈意见"
    )

    # 反馈时间
    feedback_time = models.DateTimeField(
        verbose_name="反馈时间",
        help_text="反馈提交时间",
        db_comment="反馈提交时间"
    )

    class Meta:
        db_table = CUS_TABLE_PREFIX + "ai_audit_feedback"
        verbose_name = "AI审核反馈"
        verbose_name_plural = verbose_name
        ordering = ['-feedback_time']
        indexes = [
            models.Index(fields=['audit_log_id'], name='idx_feedback_audit_log'),
            models.Index(fields=['reviewer_id'], name='idx_feedback_reviewer'),
            models.Index(fields=['manual_conclusion'], name='idx_manual_conclusion'),
            models.Index(fields=['final_result'], name='idx_final_result'),
            models.Index(fields=['feedback_time'], name='idx_feedback_time'),
        ]

    def __str__(self):
        return f"反馈-{self.audit_log_id} - {self.get_manual_conclusion_display()}"
