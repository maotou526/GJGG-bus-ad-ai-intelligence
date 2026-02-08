from django.core.management.base import BaseCommand
from bs_notice.services import NoticeService


class Command(BaseCommand):
    help = 'Send a test notification to specific users'

    def handle(self, *args, **options):
        notice = NoticeService.send_notification(
            msg_type=1,
            title='测试通知',
            content='这是一个测试的消息通知',
            priority=2,
            send_type=1,
            extra_data={
                'user_ids': [
                    'e9cee88c-4020-41e4-a95e-2829fbc5554d',
                    '95062d71-7988-45a8-bdb0-9d5e656e58c5',
                ]
            },
            sender_name='超级管理员',
        )
        self.stdout.write(self.style.SUCCESS(
            f'OK! notice.id={notice.id}, title={notice.title}'
        ))
