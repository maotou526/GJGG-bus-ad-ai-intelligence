"""
AI审核辅助函数
Description: 提供AI审核相关的辅助功能
Version: 1.0
Date: 2026-02-03
"""
from datetime import datetime
from ..constants import AUDIT_NO_PREFIX


def generate_audit_no():
    """
    生成审核编号
    格式：AUD-YYYYMMDD-XXXX

    Returns:
        str: 审核编号
    """
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    microsecond = now.microsecond // 1000  # 毫秒部分

    # 格式：AUD-YYYYMMDD-HHMMSS-MS
    audit_no = f"{AUDIT_NO_PREFIX}-{date_str}-{time_str}{microsecond:03d}"

    return audit_no


def calculate_duration(request_time, response_time):
    """
    计算审核耗时

    Args:
        request_time: 请求时间
        response_time: 响应时间

    Returns:
        int: 耗时秒数，如果无法计算返回None
    """
    if not request_time or not response_time:
        return None

    try:
        duration = (response_time - request_time).total_seconds()
        return int(duration)
    except Exception:
        return None


def determine_need_manual_review(ai_conclusion, risk_level, confidence_score):
    """
    判断是否需要人工复核

    业务规则：
    1. AI判定为"疑似违规"或"明确违规" → 需要人工复核
    2. 风险等级为"中风险"或"高风险" → 需要人工复核
    3. 置信度低于60分 → 需要人工复核
    4. 审核失败 → 需要人工复核

    Args:
        ai_conclusion: AI判定结果（1:通过, 2:疑似违规, 3:明确违规, 4:审核失败）
        risk_level: 风险等级（1:无风险, 2:低风险, 3:中风险, 4:高风险）
        confidence_score: 置信度分数（0-100）

    Returns:
        bool: True需要人工复核, False不需要
    """
    # 审核失败必须人工复核
    if ai_conclusion == 4:
        return True

    # 疑似违规或明确违规需要人工复核
    if ai_conclusion in [2, 3]:
        return True

    # 中风险或高风险需要人工复核
    if risk_level in [3, 4]:
        return True

    # 置信度低于60分需要人工复核
    if confidence_score and confidence_score < 60:
        return True

    return False
