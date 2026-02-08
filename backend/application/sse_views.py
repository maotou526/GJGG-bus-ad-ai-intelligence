# views.py
import time

import jwt
from django.http import StreamingHttpResponse

from application import settings
from dvadmin.system.models import MessageCenterTargetUser
from django.core.cache import cache


def event_stream(user_id):
    last_sent_time = 0

    while True:
        try:
            # 从 Redis 中获取最后数据库变更时间
            last_db_change_time = cache.get('last_db_change_time', 0)
            # 只有当数据库发生变化时才检查总数
            if last_db_change_time and last_db_change_time > last_sent_time:
                count = MessageCenterTargetUser.objects.filter(users=user_id, is_read=False).count()
                yield f"data: {count}\n\n"
                last_sent_time = time.time()
        except Exception as e:
            # Redis 连接失败时，使用降级策略：定期检查消息数量
            # 每5秒检查一次，避免频繁查询数据库
            if time.time() - last_sent_time >= 5:
                try:
                    count = MessageCenterTargetUser.objects.filter(users=user_id, is_read=False).count()
                    yield f"data: {count}\n\n"
                    last_sent_time = time.time()
                except Exception as db_error:
                    # 数据库查询也失败时，发送错误信息
                    yield f"data: error\n\n"
                    break

        time.sleep(1)


def sse_view(request):
    token = request.GET.get('token')
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    user_id = decoded.get('user_id')
    response = StreamingHttpResponse(event_stream(user_id), content_type='text/event-stream')
    response['Cache-Control'] = 'no-cache'
    return response
