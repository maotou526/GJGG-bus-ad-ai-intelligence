"""
AI审核记录序列化器
Description: AI审核记录的序列化和反序列化
Version: 1.0
Date: 2026-02-03
"""
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import AIAuditLogModel
from ..utils.audit_enums import (
    AUDIT_SOURCE_CHOICES, AUDIT_TYPE_CHOICES, AI_CONCLUSION_CHOICES, RISK_LEVEL_CHOICES
)


class AIAuditLogSerializer(CustomModelSerializer):
    """
    AI审核记录序列化器

    功能说明：
    - 提供AI审核记录的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 自动计算显示字段（审核来源名称、审核类型名称等）
    - 提供数据验证功能
    """

    # 计算字段 - 审核来源名称
    audit_source_display = serializers.SerializerMethodField()

    # 计算字段 - 审核类型名称
    audit_type_display = serializers.SerializerMethodField()

    # 计算字段 - AI判定结果名称
    ai_conclusion_display = serializers.SerializerMethodField()

    # 计算字段 - 风险等级名称
    risk_level_display = serializers.SerializerMethodField()

    class Meta:
        model = AIAuditLogModel
        fields = "__all__"
        read_only_fields = ["id", "audit_no", "duration_seconds", "need_manual_review",
                           "create_datetime", "update_datetime"]
        extra_kwargs = {
            "raw_response": {"write_only": True},  # 原始响应只在写入时使用，不在响应中显示
            "audit_source": {"required": True},
            "file_path": {"required": True},
            "audit_type": {"required": True},
            "request_time": {"required": False, "allow_null": True},
            "ai_conclusion": {"required": True},
            "detection_details": {"required": False, "allow_null": True},
            "violation_content": {"required": False, "allow_null": True},
        }

    def get_audit_source_display(self, obj):
        """获取审核来源名称"""
        return AUDIT_SOURCE_CHOICES.get(obj.audit_source, "未知")

    def get_audit_type_display(self, obj):
        """获取审核类型名称"""
        return AUDIT_TYPE_CHOICES.get(obj.audit_type, "未知")

    def get_ai_conclusion_display(self, obj):
        """获取AI判定结果名称"""
        return AI_CONCLUSION_CHOICES.get(obj.ai_conclusion, "未知")

    def get_risk_level_display(self, obj):
        """获取风险等级名称"""
        if obj.risk_level:
            return RISK_LEVEL_CHOICES.get(obj.risk_level, "未知")
        return None

    def validate_audit_source(self, value):
        """验证审核来源"""
        if value not in AUDIT_SOURCE_CHOICES:
            raise serializers.ValidationError("无效的审核来源")
        return value

    def validate_audit_type(self, value):
        """验证审核类型"""
        if value not in AUDIT_TYPE_CHOICES:
            raise serializers.ValidationError("无效的审核类型")
        return value

    def validate_ai_conclusion(self, value):
        """验证AI判定结果"""
        if value not in AI_CONCLUSION_CHOICES:
            raise serializers.ValidationError("无效的AI判定结果")
        return value

    def validate_risk_level(self, value):
        """验证风险等级"""
        if value is not None and value not in RISK_LEVEL_CHOICES:
            raise serializers.ValidationError("无效的风险等级")
        return value

    def validate_confidence_score(self, value):
        """验证置信度分数"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("置信度必须在0-100之间")
        return value

    def validate(self, attrs):
        """整体验证"""
        # 验证关联订单审核时必须有material_id
        audit_source = attrs.get("audit_source")
        material_id = attrs.get("material_id")

        if audit_source == 1 and not material_id:  # 关联订单审核
            raise serializers.ValidationError("关联订单审核必须提供材料ID")

        if audit_source == 2 and material_id:  # 独立审核
            raise serializers.ValidationError("独立审核不应提供材料ID")

        return attrs


class AIAuditLogCreateSerializer(AIAuditLogSerializer):
    """
    AI审核记录创建序列化器

    功能说明：
    - 专门用于创建新审核记录时的数据验证
    - 设置创建时的必填字段
    """

    class Meta(AIAuditLogSerializer.Meta):
        extra_kwargs = {
            **AIAuditLogSerializer.Meta.extra_kwargs,
            "audit_source": {"required": True},
            "file_path": {"required": True},
            "audit_type": {"required": True},
            "ai_conclusion": {"required": True},
        }


class AIAuditLogUpdateSerializer(AIAuditLogSerializer):
    """
    AI审核记录更新序列化器

    功能说明：
    - 专门用于更新现有审核记录时的数据验证
    - 防止修改关键字段
    """

    class Meta(AIAuditLogSerializer.Meta):
        read_only_fields = [
            "id", "audit_no", "audit_source", "material_id", "order_id",
            "file_path", "audit_type", "platform", "request_time",
            "duration_seconds", "need_manual_review",
            "create_datetime", "update_datetime"
        ]


class AIAuditLogListSerializer(AIAuditLogSerializer):
    """
    AI审核记录列表序列化器

    功能说明：
    - 专门用于审核记录列表显示
    - 返回必要字段和计算字段
    - 隐藏原始响应等敏感数据
    """

    class Meta(AIAuditLogSerializer.Meta):
        fields = [
            "id", "audit_no", "audit_source", "audit_source_display",
            "material_id", "order_id", "file_name", "audit_type", "audit_type_display",
            "platform", "request_time", "response_time", "duration_seconds",
            "ai_conclusion", "ai_conclusion_display", "risk_level", "risk_level_display",
            "confidence_score", "need_manual_review", "summary", "error_message",
            "create_datetime", "update_datetime", "creator_name"
        ]
        read_only_fields = fields


class AIAuditLogDetailSerializer(AIAuditLogSerializer):
    """
    AI审核记录详情序列化器

    功能说明：
    - 用于查看审核记录详细信息
    - 包含检测项详情、违规内容等完整信息
    - 返回所有字段（除了raw_response）
    """

    class Meta(AIAuditLogSerializer.Meta):
        fields = [
            "id", "audit_no", "audit_source", "audit_source_display",
            "material_id", "order_id", "file_name", "file_path",
            "audit_type", "audit_type_display", "platform", "agent_id_ext",
            "request_time", "response_time", "duration_seconds",
            "ai_conclusion", "ai_conclusion_display",
            "risk_level", "risk_level_display", "confidence_score",
            "detection_details", "violation_content", "summary",
            "error_message", "need_manual_review",
            "create_datetime", "update_datetime",
            "creator_name", "modifier_name", "description"
        ]
        read_only_fields = fields


class AIAuditLogSimpleSerializer(CustomModelSerializer):
    """
    AI审核记录简单序列化器

    功能说明：
    - 只返回核心字段
    - 用于下拉选择、关联查询等场景
    """

    audit_source_display = serializers.SerializerMethodField()
    ai_conclusion_display = serializers.SerializerMethodField()

    class Meta:
        model = AIAuditLogModel
        fields = [
            "id", "audit_no", "audit_source", "audit_source_display",
            "ai_conclusion", "ai_conclusion_display", "confidence_score",
            "need_manual_review", "create_datetime"
        ]
        read_only_fields = fields

    def get_audit_source_display(self, obj):
        """获取审核来源名称"""
        return AUDIT_SOURCE_CHOICES.get(obj.audit_source, "未知")

    def get_ai_conclusion_display(self, obj):
        """获取AI判定结果名称"""
        return AI_CONCLUSION_CHOICES.get(obj.ai_conclusion, "未知")
