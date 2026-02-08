"""
AI审核反馈序列化器
Description: AI审核反馈的序列化和反序列化
Version: 1.0
Date: 2026-02-03
"""
from rest_framework import serializers
from django.utils import timezone
from dvadmin.utils.serializers import CustomModelSerializer
from .models import AIAuditFeedbackModel
from ..utils.audit_enums import (
    MANUAL_CONCLUSION_CHOICES, FINAL_RESULT_CHOICES, AI_ACCURACY_CHOICES
)


class AIAuditFeedbackSerializer(CustomModelSerializer):
    """
    AI审核反馈序列化器

    功能说明：
    - 提供AI审核反馈的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 自动计算显示字段
    """

    # 计算字段 - 人工判定结果名称
    manual_conclusion_display = serializers.SerializerMethodField()

    # 计算字段 - 最终审核结果名称
    final_result_display = serializers.SerializerMethodField()

    # 计算字段 - AI准确性名称
    ai_accuracy_display = serializers.SerializerMethodField()

    class Meta:
        model = AIAuditFeedbackModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "audit_log_id": {"required": True},
            "reviewer_id": {"required": True},
            "manual_conclusion": {"required": True},
            "final_result": {"required": True},
            "feedback_time": {"required": False, "allow_null": True},
        }

    def get_manual_conclusion_display(self, obj):
        """获取人工判定结果名称"""
        return MANUAL_CONCLUSION_CHOICES.get(obj.manual_conclusion, "未知")

    def get_final_result_display(self, obj):
        """获取最终审核结果名称"""
        return FINAL_RESULT_CHOICES.get(obj.final_result, "未知")

    def get_ai_accuracy_display(self, obj):
        """获取AI准确性名称"""
        if obj.ai_accuracy:
            return AI_ACCURACY_CHOICES.get(obj.ai_accuracy, "未知")
        return None

    def validate_manual_conclusion(self, value):
        """验证人工判定结果"""
        if value not in MANUAL_CONCLUSION_CHOICES:
            raise serializers.ValidationError("无效的人工判定结果")
        return value

    def validate_final_result(self, value):
        """验证最终审核结果"""
        if value not in FINAL_RESULT_CHOICES:
            raise serializers.ValidationError("无效的最终审核结果")
        return value

    def validate_ai_accuracy(self, value):
        """验证AI准确性"""
        if value is not None and value not in AI_ACCURACY_CHOICES:
            raise serializers.ValidationError("无效的AI准确性评分")
        return value

    def validate_audit_log_id(self, value):
        """验证审核记录ID"""
        # 检查是否已存在该审核记录的反馈
        if self.instance is None:  # 创建时检查
            if AIAuditFeedbackModel.objects.filter(audit_log_id=value, delete_mark=0).exists():
                raise serializers.ValidationError("该审核记录已有反馈，不能重复提交")
        return value

    def create(self, validated_data):
        """创建反馈时自动设置反馈时间"""
        if 'feedback_time' not in validated_data or not validated_data['feedback_time']:
            validated_data['feedback_time'] = timezone.now()
        return super().create(validated_data)


class AIAuditFeedbackCreateSerializer(AIAuditFeedbackSerializer):
    """
    AI审核反馈创建序列化器

    功能说明：
    - 专门用于创建新反馈时的数据验证
    - 设置创建时的必填字段
    """

    class Meta(AIAuditFeedbackSerializer.Meta):
        extra_kwargs = {
            **AIAuditFeedbackSerializer.Meta.extra_kwargs,
            "audit_log_id": {"required": True},
            "reviewer_id": {"required": True},
            "manual_conclusion": {"required": True},
            "final_result": {"required": True},
        }


class AIAuditFeedbackUpdateSerializer(AIAuditFeedbackSerializer):
    """
    AI审核反馈更新序列化器

    功能说明：
    - 专门用于更新现有反馈时的数据验证
    - 防止修改关键字段
    """

    class Meta(AIAuditFeedbackSerializer.Meta):
        read_only_fields = [
            "id", "audit_log_id", "reviewer_id", "feedback_time",
            "create_datetime", "update_datetime"
        ]


class AIAuditFeedbackListSerializer(AIAuditFeedbackSerializer):
    """
    AI审核反馈列表序列化器

    功能说明：
    - 专门用于反馈列表显示
    - 返回必要字段和计算字段
    """

    class Meta(AIAuditFeedbackSerializer.Meta):
        fields = [
            "id", "audit_log_id", "reviewer_id", "reviewer_name",
            "manual_conclusion", "manual_conclusion_display",
            "final_result", "final_result_display",
            "ai_accuracy", "ai_accuracy_display",
            "feedback_text", "feedback_time",
            "create_datetime", "creator_name"
        ]
        read_only_fields = fields


class AIAuditFeedbackDetailSerializer(AIAuditFeedbackSerializer):
    """
    AI审核反馈详情序列化器

    功能说明：
    - 用于查看反馈详细信息
    - 包含误判项、漏检项等完整信息
    """

    class Meta(AIAuditFeedbackSerializer.Meta):
        fields = [
            "id", "audit_log_id", "reviewer_id", "reviewer_name",
            "manual_conclusion", "manual_conclusion_display",
            "final_result", "final_result_display",
            "ai_accuracy", "ai_accuracy_display",
            "false_detections", "missed_detections",
            "feedback_text", "feedback_time",
            "create_datetime", "update_datetime",
            "creator_name", "modifier_name", "description"
        ]
        read_only_fields = fields
