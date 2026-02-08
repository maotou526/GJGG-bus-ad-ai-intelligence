'''
Description: 基础日期 Celery 任务
Version: 1.0
Autor: 王晨
Date: 2025-11-19 17:14:26
LastEditors: 王晨
LastEditTime: 2025-11-20 14:14:35
'''
import logging

from application.celery import app
from dvadmin_twodev.basedata.date.models import BaseDateModel

# logger = logging.getLogger(__name__)
logger = logging.getLogger('celery.task')

DATE_TYPE_MAP = {
    0: '工作日',
    1: '休息日',
}


@app.task()
def task__date_out():
    """
    输出前 10 条日期数据
    """
    records = list(BaseDateModel.objects.order_by('date')[:10])
    if not records:
        logger.info('BaseDateModel 暂无数据')
        return []

    result = []
    for record in records:
        record_date = record.date
        if isinstance(record_date, str):
            date_str = record_date
        elif hasattr(record_date, 'isoformat'):
            date_str = record_date.isoformat()
        else:
            date_str = str(record_date)

        info = {
            'date': date_str,
            'date_type': DATE_TYPE_MAP.get(record.date_type, '未知'),
            'name': record.name or '',
            'is_work': bool(record.is_work),
        }
        message = (
            f"日期：{info['date']} | 类型：{info['date_type']} | "
            f"名称：{info['name'] or '-'} | 是否上班：{info['is_work']}"
        )
        logger.info(message)
        print(message)
        result.append(info)

    return result
 
