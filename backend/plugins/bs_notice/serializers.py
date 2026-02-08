"""
Description: 消息通知序列化器
Version: 1.0
Autor: AI Assistant
Date: 2026-02-05
LastEditors: 
LastEditTime: 2026-02-05
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import NoticeModel, NoticeUserModel


class NoticeModelSerializer(CustomModelSerializer):
    """
    消息主表序列化器
    """
    
    # 计算字段 - 消息类型显示名称
    msg_type_display = serializers.SerializerMethodField()
    
    # 计算字段 - 优先级显示名称
    priority_display = serializers.SerializerMethodField()
    
    # 计算字段 - 发送方式显示名称
    send_type_display = serializers.SerializerMethodField()
    
    # 计算字段 - 是否过期
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = NoticeModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime", "send_time"]
        extra_kwargs = {
            "msg_type": {"required": True, "allow_null": False},
            "title": {"required": True, "allow_null": False, "allow_blank": False},
            "priority": {"required": False, "allow_null": False, "default": 2},
            "send_type": {"required": True, "allow_null": False},
            "rec_table": {"required": False, "allow_null": True, "allow_blank": True},
            "rec_id": {"required": False, "allow_null": True, "allow_blank": True},
            "content": {"required": False, "allow_null": True, "allow_blank": True},
            "jump_url": {"required": False, "allow_null": True, "allow_blank": True},
            "sender_id": {"required": False, "allow_null": True, "allow_blank": True},
            "sender_name": {"required": False, "allow_null": True, "allow_blank": True},
            "expire_time": {"required": False, "allow_null": True},
            "extra_data": {"required": False, "allow_null": True},
        }
    
    def get_msg_type_display(self, obj):
        """消息类型显示名称"""
        return obj.get_msg_type_display()
    
    def get_priority_display(self, obj):
        """优先级显示名称"""
        return obj.get_priority_display()
    
    def get_send_type_display(self, obj):
        """发送方式显示名称"""
        return obj.get_send_type_display()
    
    def get_is_expired(self, obj):
        """是否过期"""
        return obj.is_expired()
    
    def validate_msg_type(self, value):
        """验证消息类型"""
        if value not in [1, 2, 3, 4]:
            raise serializers.ValidationError("消息类型只能是：1=系统通知, 2=业务消息, 3=告警消息, 4=待办提醒")
        return value
    
    def validate_send_type(self, value):
        """验证发送方式"""
        if value not in [1, 2, 3, 4, 5]:
            raise serializers.ValidationError("发送方式只能是：1=指定用户, 2=指定角色, 3=指定部门, 4=全局广播, 5=混合模式")
        return value
    
    def validate_priority(self, value):
        """验证优先级"""
        if value not in [1, 2, 3]:
            raise serializers.ValidationError("优先级只能是：1=紧急, 2=普通, 3=低")
        return value


class NoticeModelCreateSerializer(NoticeModelSerializer):
    """
    消息创建序列化器
    """
    
    class Meta(NoticeModelSerializer.Meta):
        pass


class NoticeModelUpdateSerializer(NoticeModelSerializer):
    """
    消息更新序列化器
    """
    
    class Meta(NoticeModelSerializer.Meta):
        read_only_fields = ["id", "create_datetime", "update_datetime", "send_time"]


class NoticeModelListSerializer(NoticeModelSerializer):
    """
    消息列表序列化器
    """
    
    class Meta:
        model = NoticeModel
        fields = [
            "id",
            "msg_type",
            "msg_type_display",
            "rec_table",
            "rec_id",
            "title",
            "content",
            "jump_url",
            "priority",
            "priority_display",
            "send_type",
            "send_type_display",
            "sender_id",
            "sender_name",
            "send_time",
            "expire_time",
            "is_expired",
            "extra_data",
            "create_datetime",
            "update_datetime",
            "enabled_mark",
            "delete_mark",
        ]
        read_only_fields = fields


class NoticeUserModelSerializer(CustomModelSerializer):
    """
    用户消息关联序列化器
    """
    
    # 计算字段 - 阅读状态显示名称
    read_status_display = serializers.SerializerMethodField()
    
    # 计算字段 - 处理状态显示名称
    handle_status_display = serializers.SerializerMethodField()
    
    # 关联消息详情（可选）
    notice_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = NoticeUserModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "notice_id": {"required": True, "allow_null": False, "allow_blank": False},
            "user_id": {"required": True, "allow_null": False, "allow_blank": False},
            "user_name": {"required": False, "allow_null": True, "allow_blank": True},
            "read_status": {"required": False, "allow_null": False, "default": 0},
            "read_time": {"required": False, "allow_null": True},
            "handle_status": {"required": False, "allow_null": False, "default": 0},
            "handle_time": {"required": False, "allow_null": True},
        }
    
    def get_read_status_display(self, obj):
        """阅读状态显示名称"""
        return obj.get_read_status_display()
    
    def get_handle_status_display(self, obj):
        """处理状态显示名称"""
        return obj.get_handle_status_display()
    
    def get_notice_detail(self, obj):
        """关联消息详情"""
        try:
            notice = NoticeModel.objects.get(id=obj.notice_id)
            return NoticeModelListSerializer(notice).data
        except NoticeModel.DoesNotExist:
            return None


class NoticeUserModelCreateSerializer(NoticeUserModelSerializer):
    """
    用户消息关联创建序列化器
    """
    
    class Meta(NoticeUserModelSerializer.Meta):
        pass


class NoticeUserModelUpdateSerializer(NoticeUserModelSerializer):
    """
    用户消息关联更新序列化器
    """
    
    class Meta(NoticeUserModelSerializer.Meta):
        read_only_fields = ["id", "create_datetime", "update_datetime", "notice_id", "user_id"]


class NoticeUserModelListSerializer(NoticeUserModelSerializer):
    """
    用户消息关联列表序列化器
    将关联的通知主表字段平铺返回，前端可直接使用
    """
    title = serializers.SerializerMethodField()
    msg_type = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()
    priority = serializers.SerializerMethodField()
    sender_name = serializers.SerializerMethodField()
    send_time = serializers.SerializerMethodField()
    jump_url = serializers.SerializerMethodField()
    rec_table = serializers.SerializerMethodField()
    rec_id = serializers.SerializerMethodField()

    class Meta:
        model = NoticeUserModel
        fields = [
            "id",
            "notice_id",
            "user_id",
            "user_name",
            "read_status",
            "read_status_display",
            "read_time",
            "handle_status",
            "handle_status_display",
            "handle_time",
            "title",
            "msg_type",
            "content",
            "priority",
            "sender_name",
            "send_time",
            "jump_url",
            "rec_table",
            "rec_id",
            "create_datetime",
            "update_datetime",
        ]
        read_only_fields = fields

    def _get_notice(self, obj):
        if not hasattr(obj, '_cached_notice'):
            try:
                obj._cached_notice = NoticeModel.objects.get(id=obj.notice_id)
            except NoticeModel.DoesNotExist:
                obj._cached_notice = None
        return obj._cached_notice

    def get_title(self, obj):
        notice = self._get_notice(obj)
        return notice.title if notice else None

    def get_msg_type(self, obj):
        notice = self._get_notice(obj)
        return notice.msg_type if notice else None

    def get_content(self, obj):
        notice = self._get_notice(obj)
        return notice.content if notice else None

    def get_priority(self, obj):
        notice = self._get_notice(obj)
        return notice.priority if notice else None

    def get_sender_name(self, obj):
        notice = self._get_notice(obj)
        return notice.sender_name if notice else None

    def get_send_time(self, obj):
        notice = self._get_notice(obj)
        return notice.send_time if notice else None

    def get_jump_url(self, obj):
        notice = self._get_notice(obj)
        return notice.jump_url if notice else None

    def get_rec_table(self, obj):
        notice = self._get_notice(obj)
        return notice.rec_table if notice else None

    def get_rec_id(self, obj):
        notice = self._get_notice(obj)
        return notice.rec_id if notice else None

