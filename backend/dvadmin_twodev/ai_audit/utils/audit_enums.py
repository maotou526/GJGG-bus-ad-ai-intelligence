"""
AI审核枚举类定义
Description: 定义AI审核相关的枚举常量
Version: 1.0
Date: 2026-02-03
"""
from enum import IntEnum


class AuditSource(IntEnum):
    """审核来源"""
    RELATED_ORDER = 1  # 关联订单审核
    STANDALONE = 2  # 独立审核


class AuditType(IntEnum):
    """审核类型"""
    CONTENT = 1  # 画面内容审核
    DOCUMENT = 2  # 证明文件审核
    COMPREHENSIVE = 3  # 综合审核


class AIConclusion(IntEnum):
    """AI判定结果"""
    PASS = 1  # 通过
    SUSPECTED_VIOLATION = 2  # 疑似违规
    CLEAR_VIOLATION = 3  # 明确违规
    FAILED = 4  # 审核失败


class RiskLevel(IntEnum):
    """风险等级"""
    NO_RISK = 1  # 无风险
    LOW_RISK = 2  # 低风险
    MEDIUM_RISK = 3  # 中风险
    HIGH_RISK = 4  # 高风险


class ManualConclusion(IntEnum):
    """人工判定结果"""
    AGREE = 1  # 同意AI判定
    PARTIAL_AGREE = 2  # 部分同意
    DISAGREE = 3  # 完全不同意


class FinalResult(IntEnum):
    """最终审核结果"""
    PASS = 1  # 通过
    REJECT = 2  # 驳回修改
    TO_LEGAL = 3  # 转法务审核


class AIAccuracy(IntEnum):
    """AI判定准确性"""
    VERY_ACCURATE = 1  # 非常准确
    BASICALLY_ACCURATE = 2  # 基本准确
    NOT_VERY_ACCURATE = 3  # 不太准确
    COMPLETELY_WRONG = 4  # 完全错误


# 枚举中文映射字典
AUDIT_SOURCE_CHOICES = {
    AuditSource.RELATED_ORDER: "关联订单审核",
    AuditSource.STANDALONE: "独立审核"
}

AUDIT_TYPE_CHOICES = {
    AuditType.CONTENT: "画面内容审核",
    AuditType.DOCUMENT: "证明文件审核",
    AuditType.COMPREHENSIVE: "综合审核"
}

AI_CONCLUSION_CHOICES = {
    AIConclusion.PASS: "通过",
    AIConclusion.SUSPECTED_VIOLATION: "疑似违规",
    AIConclusion.CLEAR_VIOLATION: "明确违规",
    AIConclusion.FAILED: "审核失败"
}

RISK_LEVEL_CHOICES = {
    RiskLevel.NO_RISK: "无风险",
    RiskLevel.LOW_RISK: "低风险",
    RiskLevel.MEDIUM_RISK: "中风险",
    RiskLevel.HIGH_RISK: "高风险"
}

MANUAL_CONCLUSION_CHOICES = {
    ManualConclusion.AGREE: "同意AI判定",
    ManualConclusion.PARTIAL_AGREE: "部分同意",
    ManualConclusion.DISAGREE: "完全不同意"
}

FINAL_RESULT_CHOICES = {
    FinalResult.PASS: "通过",
    FinalResult.REJECT: "驳回修改",
    FinalResult.TO_LEGAL: "转法务审核"
}

AI_ACCURACY_CHOICES = {
    AIAccuracy.VERY_ACCURATE: "非常准确",
    AIAccuracy.BASICALLY_ACCURATE: "基本准确",
    AIAccuracy.NOT_VERY_ACCURATE: "不太准确",
    AIAccuracy.COMPLETELY_WRONG: "完全错误"
}
