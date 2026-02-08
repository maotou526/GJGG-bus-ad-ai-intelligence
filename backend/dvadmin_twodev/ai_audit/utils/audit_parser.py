"""
审核结果解析工具
Description: 解析和处理审核结果数据
Version: 1.0
Date: 2026-02-03
"""
from typing import Dict, List, Any, Optional
import json


def parse_detection_details(details: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    解析检测项详情

    Args:
        details: 原始检测项列表

    Returns:
        List: 格式化后的检测项列表

    示例输出：
    [
        {
            "item_name": "违禁词检测",
            "item_code": "prohibited_words",
            "result": "pass",
            "confidence": 95.5,
            "details": "未检测到违禁词"
        }
    ]
    """
    if not details:
        return []

    formatted_details = []
    for item in details:
        formatted_item = {
            "item_name": item.get("item_name", "未知检测项"),
            "item_code": item.get("item_code", "unknown"),
            "result": item.get("result", "unknown"),
            "confidence": float(item.get("confidence", 0)),
        }

        # 添加其他字段
        for key in ["details", "detected_words", "positions", "resolution", "dpi"]:
            if key in item:
                formatted_item[key] = item[key]

        formatted_details.append(formatted_item)

    return formatted_details


def parse_violation_content(violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    解析违规内容

    Args:
        violations: 原始违规内容列表

    Returns:
        List: 格式化后的违规内容列表

    示例输出：
    [
        {
            "violation_type": "绝对化用语",
            "violation_code": "absolute_expression",
            "severity": "medium",
            "content": "全国第一品牌",
            "regulation": "《广告法》第九条",
            "position": {"x": 120, "y": 340, "w": 150, "h": 30},
            "suggestion": "建议修改为：知名品牌"
        }
    ]
    """
    if not violations:
        return []

    formatted_violations = []
    for item in violations:
        formatted_item = {
            "violation_type": item.get("violation_type", "未知违规"),
            "violation_code": item.get("violation_code", "unknown"),
            "severity": item.get("severity", "low"),
            "content": item.get("content", ""),
        }

        # 添加其他字段
        for key in ["regulation", "position", "suggestion", "confidence"]:
            if key in item:
                formatted_item[key] = item[key]

        formatted_violations.append(formatted_item)

    return formatted_violations


def calculate_overall_risk_level(
    ai_conclusion: int,
    violations: List[Dict[str, Any]],
    detection_details: List[Dict[str, Any]]
) -> int:
    """
    计算综合风险等级

    Args:
        ai_conclusion: AI判定结果（1:通过, 2:疑似违规, 3:明确违规, 4:审核失败）
        violations: 违规内容列表
        detection_details: 检测项详情列表

    Returns:
        int: 风险等级（1:无风险, 2:低风险, 3:中风险, 4:高风险）
    """
    # 审核失败，风险未知，返回中风险
    if ai_conclusion == 4:
        return 3

    # 明确违规，检查严重程度
    if ai_conclusion == 3:
        high_severity_count = sum(1 for v in violations if v.get("severity") == "high")
        if high_severity_count > 0:
            return 4  # 高风险
        return 3  # 中风险

    # 疑似违规
    if ai_conclusion == 2:
        return 2  # 低风险

    # 通过
    return 1  # 无风险


def calculate_overall_confidence(detection_details: List[Dict[str, Any]]) -> Optional[float]:
    """
    计算综合置信度

    Args:
        detection_details: 检测项详情列表

    Returns:
        float: 平均置信度（0-100）
    """
    if not detection_details:
        return None

    confidences = [item.get("confidence", 0) for item in detection_details if "confidence" in item]

    if not confidences:
        return None

    return round(sum(confidences) / len(confidences), 2)


def format_audit_result(raw_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    格式化审核结果

    Args:
        raw_result: 原始审核结果

    Returns:
        Dict: 格式化后的审核结果
    """
    detection_details = parse_detection_details(raw_result.get("detection_details", []))
    violation_content = parse_violation_content(raw_result.get("violations", []))

    ai_conclusion = raw_result.get("ai_conclusion", raw_result.get("conclusion", 1))

    # 计算综合风险等级
    risk_level = raw_result.get("risk_level")
    if risk_level is None:
        risk_level = calculate_overall_risk_level(ai_conclusion, violation_content, detection_details)

    # 计算综合置信度
    confidence_score = raw_result.get("confidence_score", raw_result.get("confidence"))
    if confidence_score is None:
        confidence_score = calculate_overall_confidence(detection_details)

    return {
        "ai_conclusion": ai_conclusion,
        "risk_level": risk_level,
        "confidence_score": confidence_score,
        "detection_details": detection_details,
        "violation_content": violation_content,
        "raw_response": raw_result.get("raw_response", json.dumps(raw_result, ensure_ascii=False)),
        "error_message": raw_result.get("error_message")
    }
