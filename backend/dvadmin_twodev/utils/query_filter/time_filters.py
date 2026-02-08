"""
时间相关的通用查询过滤器构造函数

主要用于根据业务定义的时间段（如早高峰/晚高峰/平峰）构建 Django Q 对象。
"""

from django.db.models import Q

from dvadmin_twodev.constants.business_constants import TIME_PERIOD_RULES


def build_time_filter(field_name: str, time_period: str) -> Q:
    """
    根据时间段构建过滤条件 Q 对象。

    参数:
        field_name: 用于过滤的时间字段名，例如 "departure_time"
        time_period: 时间段标识，支持：
            - None / "" / "all" / "全天"：不过滤时间段
            - "morning_peak" / "早高峰" / "7-9" / "7-9时"
            - "evening_peak" / "晚高峰" / "17-19" / "17-19时"
            - "off_peak" / "平峰" / "平峰时段"（排除早/晚高峰，其余时间）

    返回:
        Django Q 对象，可用于 QuerySet.filter(...)
    """
    if not time_period or time_period in ("all", "全天"):
        return Q()

    tp = str(time_period).strip().lower()

    if tp in ("morning_peak", "早高峰", "7-9", "7-9时"):
        start, end = TIME_PERIOD_RULES["morning_peak"]
        return Q(**{f"{field_name}__gte": start, f"{field_name}__lt": end})

    if tp in ("evening_peak", "晚高峰", "17-19", "17-19时"):
        start, end = TIME_PERIOD_RULES["evening_peak"]
        return Q(**{f"{field_name}__gte": start, f"{field_name}__lt": end})

    if tp in ("off_peak", "平峰", "平峰时段"):
        # 平峰：排除早晚高峰
        mp_start, mp_end = TIME_PERIOD_RULES["morning_peak"]
        ep_start, ep_end = TIME_PERIOD_RULES["evening_peak"]
        return ~(
            Q(**{f"{field_name}__gte": mp_start, f"{field_name}__lt": mp_end})
            | Q(**{f"{field_name}__gte": ep_start, f"{field_name}__lt": ep_end})
        )

    # 未识别的时间段，默认不过滤
    return Q()


