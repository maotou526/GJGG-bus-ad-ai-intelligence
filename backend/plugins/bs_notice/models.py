'''
Description: 消息通知模型
Version: 1.0
Autor: AI Assistant
Date: 2026-02-05
LastEditors: 
LastEditTime: 2026-02-05
'''
from django.db import models
from django.utils import timezone
from dvadmin_twodev.baseentity.models import BaseDataModel
from application import settings

# 消息类型
MSG_TYPE_CHOICES = (
    (1, '系统通知'),
    (2, '业务消息'),
    (3, '告警消息'),
    (4, '待办提醒'),
)

# 优先级
PRIORITY_CHOICES = (
    (1, '紧急'),
    (2, '普通'),
    (3, '低'),
)

# 发送方式
SEND_TYPE_CHOICES = (
    (1, '指定用户'),
    (2, '指定角色'),
    (3, '指定部门'),
    (4, '全局广播'),
    (5, '混合模式'),
)

# 阅读状态
READ_STATUS_CHOICES = (
    (0, '未读'),
    (1, '已读'),
)

# 处理状态
HANDLE_STATUS_CHOICES = (
    (0, '未处理'),
    (1, '已处理'),
    (2, '已忽略'),
)


class NoticeModel(BaseDataModel):
    """
    系统消息主表
    存储消息内容本身，支持一对一、一对多、全局广播
    """
    
    # 消息类型
    msg_type = models.IntegerField(
        choices=MSG_TYPE_CHOICES,
        null=False,
        blank=False,
        verbose_name="消息类型",
        help_text="1:系统通知, 2:业务消息, 3:告警消息, 4:待办提醒",
        db_comment="消息类型：1系统通知 2业务消息 3告警消息 4待办提醒"
    )
    
    # 关联业务表
    rec_table = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name="关联业务表",
        help_text="业务标识，如booking_order、on_air_order、vehicle_transfer",
        db_comment="关联业务表，业务标识"
    )
    
    # 关联业务ID
    rec_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        verbose_name="关联业务ID",
        help_text="业务记录主键ID（UUID字符串）",
        db_comment="关联业务ID，业务记录主键ID（UUID字符串）"
    )
    
    # 消息标题
    title = models.CharField(
        max_length=200,
        null=False,
        blank=False,
        verbose_name="消息标题",
        help_text="消息标题",
        db_comment="消息标题"
    )
    
    # 消息内容
    content = models.TextField(
        null=True,
        blank=True,
        verbose_name="消息内容",
        help_text="消息详细内容，支持富文本或Markdown",
        db_comment="消息内容，支持富文本或Markdown"
    )
    
    # 跳转链接
    jump_url = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="跳转链接",
        help_text="点击跳转的前端路由/URL",
        db_comment="跳转链接，前端路由或URL"
    )
    
    # 优先级
    priority = models.IntegerField(
        choices=PRIORITY_CHOICES,
        null=False,
        blank=False,
        default=2,
        verbose_name="优先级",
        help_text="1:紧急, 2:普通, 3:低（默认2）",
        db_comment="优先级：1紧急 2普通 3低"
    )
    
    # 发送方式
    send_type = models.IntegerField(
        choices=SEND_TYPE_CHOICES,
        null=False,
        blank=False,
        verbose_name="发送方式",
        help_text="1:指定用户, 2:指定角色, 3:指定部门, 4:全局广播, 5:混合模式",
        db_comment="发送方式：1指定用户 2指定角色 3指定部门 4全局广播 5混合模式"
    )
    
    # 发送人ID
    sender_id = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        verbose_name="发送人ID",
        help_text="发送人用户ID，系统消息可为空或填system",
        db_comment="发送人ID，系统消息可为空或填system"
    )
    
    # 发送人姓名
    sender_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="发送人姓名",
        help_text="发送人姓名，冗余字段",
        db_comment="发送人姓名，冗余字段"
    )
    
    # 发送时间
    send_time = models.DateTimeField(
        auto_now_add=True,
        null=False,
        blank=False,
        verbose_name="发送时间",
        help_text="消息发送时间",
        db_comment="发送时间，消息发送时间"
    )
    
    # 过期时间
    expire_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="过期时间",
        help_text="消息过期时间，过期后不再显示",
        db_comment="过期时间，过期后不再显示"
    )
    
    # 扩展数据
    extra_data = models.JSONField(
        null=True,
        blank=True,
        verbose_name="扩展数据",
        help_text="存储发送范围/附加信息，如角色ID、部门ID、用户ID列表",
        db_comment="扩展数据，存储发送范围/附加信息"
    )
    
    class Meta:
        db_table = 'bs_notice'
        verbose_name = "系统消息主表"
        verbose_name_plural = verbose_name
        ordering = ['-send_time']
        indexes = [
            models.Index(fields=['msg_type']),
            models.Index(fields=['rec_table', 'rec_id']),
            models.Index(fields=['send_time']),
            models.Index(fields=['expire_time']),
            models.Index(fields=['priority']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_msg_type_display()})"
    
    def is_expired(self):
        """检查消息是否过期"""
        if self.expire_time is None:
            return False
        return timezone.now() > self.expire_time


class NoticeUserModel(BaseDataModel):
    """
    用户消息关联表
    存储每个用户的消息接收记录、阅读状态、处理状态
    """
    
    # 消息ID
    notice_id = models.CharField(
        max_length=36,
        null=False,
        blank=False,
        verbose_name="消息ID",
        help_text="关联 bs_notice.id",
        db_comment="消息ID，关联bs_notice.id"
    )
    
    # 接收人用户ID
    user_id = models.CharField(
        max_length=36,
        null=False,
        blank=False,
        verbose_name="接收人用户ID",
        help_text="接收消息的用户ID",
        db_comment="接收人用户ID，接收消息的用户ID"
    )
    
    # 接收人姓名
    user_name = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name="接收人姓名",
        help_text="接收人姓名，冗余字段",
        db_comment="接收人姓名，冗余字段"
    )
    
    # 阅读状态
    read_status = models.IntegerField(
        choices=READ_STATUS_CHOICES,
        null=False,
        blank=False,
        default=0,
        verbose_name="阅读状态",
        help_text="0:未读, 1:已读（默认0）",
        db_comment="阅读状态：0未读 1已读"
    )
    
    # 阅读时间
    read_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="阅读时间",
        help_text="用户阅读消息的时间",
        db_comment="阅读时间，用户阅读消息的时间"
    )
    
    # 处理状态
    handle_status = models.IntegerField(
        choices=HANDLE_STATUS_CHOICES,
        null=False,
        blank=False,
        default=0,
        verbose_name="处理状态",
        help_text="0:未处理, 1:已处理, 2:已忽略（默认0）",
        db_comment="处理状态：0未处理 1已处理 2已忽略"
    )
    
    # 处理时间
    handle_time = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="处理时间",
        help_text="用户处理消息的时间",
        db_comment="处理时间，用户处理消息的时间"
    )
    
    class Meta:
        db_table = 'bs_notice_user'
        verbose_name = "用户消息关联表"
        verbose_name_plural = verbose_name
        ordering = ['-create_datetime']
        unique_together = [['notice_id', 'user_id']]
        indexes = [
            models.Index(fields=['notice_id']),
            models.Index(fields=['user_id', 'read_status', 'delete_mark']),
            models.Index(fields=['user_id', 'handle_status', 'delete_mark']),
            models.Index(fields=['user_id', 'delete_mark']),
        ]
    
    def __str__(self):
        return f"{self.user_name or self.user_id} - {self.notice_id}"
    
    def mark_as_read(self):
        """标记为已读"""
        if self.read_status == 0:
            self.read_status = 1
            self.read_time = timezone.now()
            self.save(update_fields=['read_status', 'read_time'])
    
    def mark_as_handled(self):
        """标记为已处理"""
        if self.handle_status == 0:
            self.handle_status = 1
            self.handle_time = timezone.now()
            self.save(update_fields=['handle_status', 'handle_time'])
    
    def mark_as_ignored(self):
        """标记为已忽略"""
        if self.handle_status == 0:
            self.handle_status = 2
            self.handle_time = timezone.now()
            self.save(update_fields=['handle_status', 'handle_time'])

