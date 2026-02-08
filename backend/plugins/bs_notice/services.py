"""
Description: 消息通知服务类
Version: 1.0
Autor: AI Assistant
Date: 2026-02-05
LastEditors: 
LastEditTime: 2026-02-05
"""

from django.db import transaction
from django.utils import timezone
from django.db.models import Q
from typing import List, Dict, Optional, Any
from .models import NoticeModel, NoticeUserModel
from .constants import NoticeTemplate
from dvadmin.system.models import Users, Role, Dept


class NoticeService:
    """
    消息通知服务类
    提供消息发送、查询等核心功能
    """
    
    @staticmethod
    def _resolve_receivers(send_type: int, extra_data: Dict[str, Any]) -> List[str]:
        """
        解析接收人列表
        
        Args:
            send_type: 发送方式 (1=指定用户, 2=指定角色, 3=指定部门, 4=全局广播, 5=混合模式)
            extra_data: 扩展数据，包含角色ID、部门ID、用户ID列表
            
        Returns:
            用户ID列表
        """
        user_ids = []
        
        if send_type == 1:
            # 指定用户
            user_ids = extra_data.get("user_ids", [])
        
        elif send_type == 2:
            # 指定角色
            role_ids = extra_data.get("role_ids", [])
            if role_ids:
                # 查询角色下的所有用户（角色是多对多关系）
                users = Users.objects.filter(role__id__in=role_ids, is_active=True).exclude(is_superuser=True).distinct()
                user_ids = [str(user.id) for user in users]
        
        elif send_type == 3:
            # 指定部门
            dept_ids = extra_data.get("dept_ids", [])
            if dept_ids:
                # 查询部门下的所有用户
                users = Users.objects.filter(dept_id__in=dept_ids, is_active=True).exclude(is_superuser=True)
                user_ids = [str(user.id) for user in users]
        
        elif send_type == 4:
            # 全局广播 - 查询所有活跃用户
            users = Users.objects.filter(is_active=True).exclude(is_superuser=True)
            user_ids = [str(user.id) for user in users]
        
        elif send_type == 5:
            # 混合模式：角色 + 部门 + 用户
            user_id_set = set()
            
            # 角色用户
            role_ids = extra_data.get("role_ids", [])
            if role_ids:
                users = Users.objects.filter(role__id__in=role_ids, is_active=True).exclude(is_superuser=True).distinct()
                user_id_set.update([str(user.id) for user in users])
            
            # 部门用户
            dept_ids = extra_data.get("dept_ids", [])
            if dept_ids:
                users = Users.objects.filter(dept_id__in=dept_ids, is_active=True).exclude(is_superuser=True)
                user_id_set.update([str(user.id) for user in users])
            
            # 指定用户
            direct_user_ids = extra_data.get("user_ids", [])
            if direct_user_ids:
                user_id_set.update([str(uid) for uid in direct_user_ids])
            
            user_ids = list(user_id_set)
        
        # 去重并过滤无效用户
        user_ids = list(set(user_ids))
        return user_ids
    
    @staticmethod
    @transaction.atomic
    def send_notification(
        msg_type: int,
        title: str,
        content: Optional[str] = None,
        jump_url: Optional[str] = None,
        priority: int = 2,
        send_type: int = 1,
        sender_id: Optional[str] = None,
        sender_name: Optional[str] = None,
        rec_table: Optional[str] = None,
        rec_id: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None,
        expire_time: Optional[timezone.datetime] = None,
        request=None
    ) -> NoticeModel:
        """
        发送消息
        
        Args:
            msg_type: 消息类型 (1=系统通知, 2=业务消息, 3=告警消息, 4=待办提醒)
            title: 消息标题
            content: 消息内容
            jump_url: 跳转链接
            priority: 优先级 (1=紧急, 2=普通, 3=低)
            send_type: 发送方式 (1=指定用户, 2=指定角色, 3=指定部门, 4=全局广播, 5=混合模式)
            sender_id: 发送人ID
            sender_name: 发送人姓名
            rec_table: 关联业务表
            rec_id: 关联业务ID
            extra_data: 扩展数据（角色ID、部门ID、用户ID列表）
            expire_time: 过期时间
            request: Django request对象（用于获取当前用户）
            
        Returns:
            NoticeModel实例
        """
        if extra_data is None:
            extra_data = {}
        
        # 解析接收人列表
        receiver_ids = NoticeService._resolve_receivers(send_type, extra_data)
        
        if not receiver_ids:
            raise ValueError("未找到任何接收人，请检查发送配置")
        
        # 获取发送人信息
        if request and hasattr(request, 'user') and request.user and not sender_id:
            sender_id = str(request.user.id)
            sender_name = getattr(request.user, 'name', None) or getattr(request.user, 'username', None)
        
        # 创建消息主记录
        notice = NoticeModel.objects.create(
            msg_type=msg_type,
            title=title,
            content=content,
            jump_url=jump_url,
            priority=priority,
            send_type=send_type,
            sender_id=sender_id,
            sender_name=sender_name,
            rec_table=rec_table,
            rec_id=rec_id,
            extra_data=extra_data,
            expire_time=expire_time,
        )
        
        # 批量创建用户接收记录
        notice_user_list = []
        for user_id in receiver_ids:
            # 获取用户姓名
            try:
                user = Users.objects.get(id=user_id)
                user_name = getattr(user, 'name', None) or getattr(user, 'username', None)
            except Users.DoesNotExist:
                user_name = None
            
            notice_user_list.append(
                NoticeUserModel(
                    notice_id=str(notice.id),
                    user_id=str(user_id),
                    user_name=user_name,
                    read_status=0,
                    handle_status=0,
                    delete_mark=0,
                )
            )
        
        # 批量插入
        NoticeUserModel.objects.bulk_create(notice_user_list, batch_size=500)
        
        return notice
    
    @staticmethod
    def send_by_template(
        template: Dict[str, Any],
        rec_table: Optional[str] = None,
        rec_id: Optional[str] = None,
        send_type: int = 1,
        extra_data: Optional[Dict[str, Any]] = None,
        variables: Optional[Dict[str, Any]] = None,
        sender_id: Optional[str] = None,
        sender_name: Optional[str] = None,
        expire_time: Optional[timezone.datetime] = None,
        request=None
    ) -> NoticeModel:
        """
        使用模板发送消息
        
        Args:
            template: 模板字典（来自 NoticeTemplate）
            rec_table: 关联业务表
            rec_id: 关联业务ID
            send_type: 发送方式
            extra_data: 扩展数据
            variables: 模板变量
            sender_id: 发送人ID
            sender_name: 发送人姓名
            expire_time: 过期时间
            request: Django request对象
            
        Returns:
            NoticeModel实例
        """
        if variables is None:
            variables = {}
        
        # 渲染模板
        rendered = NoticeTemplate.render(template, variables)
        
        # 发送消息
        return NoticeService.send_notification(
            msg_type=rendered["msg_type"],
            title=rendered["title"],
            content=rendered["content"],
            jump_url=rendered["jump_url"],
            priority=rendered["priority"],
            send_type=send_type,
            sender_id=sender_id,
            sender_name=sender_name,
            rec_table=rec_table,
            rec_id=rec_id,
            extra_data=extra_data,
            expire_time=expire_time,
            request=request
        )
    
    @staticmethod
    def get_unread_count(user_id: str) -> int:
        """
        获取用户未读消息数量
        
        Args:
            user_id: 用户ID
            
        Returns:
            未读消息数量
        """
        return NoticeUserModel.objects.filter(
            user_id=user_id,
            read_status=0,
            delete_mark=0
        ).count()
    
    @staticmethod
    def get_user_notices(
        user_id: str,
        msg_type: Optional[int] = None,
        read_status: Optional[int] = None,
        handle_status: Optional[int] = None,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        获取用户消息列表
        
        Args:
            user_id: 用户ID
            msg_type: 消息类型（可选）
            read_status: 阅读状态（可选）
            handle_status: 处理状态（可选）
            limit: 每页数量
            offset: 偏移量
            
        Returns:
            消息列表
        """
        # 先查询用户消息关联表
        notice_user_queryset = NoticeUserModel.objects.filter(
            user_id=user_id,
            delete_mark=0
        )
        
        # 过滤条件
        if read_status is not None:
            notice_user_queryset = notice_user_queryset.filter(read_status=read_status)
        
        if handle_status is not None:
            notice_user_queryset = notice_user_queryset.filter(handle_status=handle_status)
        
        # 获取消息ID列表
        notice_ids = list(notice_user_queryset.values_list('notice_id', flat=True))
        
        if not notice_ids:
            return []
        
        # 查询消息主表
        notice_queryset = NoticeModel.objects.filter(id__in=notice_ids)
        
        # 过滤过期消息
        notice_queryset = notice_queryset.filter(
            Q(expire_time__isnull=True) | Q(expire_time__gt=timezone.now())
        )
        
        # 过滤消息类型
        if msg_type is not None:
            notice_queryset = notice_queryset.filter(msg_type=msg_type)
        
        # 排序
        notice_queryset = notice_queryset.order_by('-send_time')
        
        # 分页
        notices = notice_queryset[offset:offset + limit]
        
        # 组装返回数据
        result = []
        for notice in notices:
            try:
                notice_user = NoticeUserModel.objects.get(
                    notice_id=str(notice.id),
                    user_id=user_id
                )
                result.append({
                    "id": notice_user.id,
                    "notice_id": notice.id,
                    "msg_type": notice.msg_type,
                    "title": notice.title,
                    "content": notice.content,
                    "jump_url": notice.jump_url,
                    "priority": notice.priority,
                    "read_status": notice_user.read_status,
                    "read_time": notice_user.read_time,
                    "handle_status": notice_user.handle_status,
                    "handle_time": notice_user.handle_time,
                    "send_time": notice.send_time,
                    "rec_table": notice.rec_table,
                    "rec_id": notice.rec_id,
                })
            except NoticeUserModel.DoesNotExist:
                continue
        
        return result
    
    @staticmethod
    def mark_as_read(notice_user_id: str, user_id: str) -> bool:
        """
        标记消息为已读
        
        Args:
            notice_user_id: 用户消息关联ID
            user_id: 用户ID（用于验证权限）
            
        Returns:
            是否成功
        """
        try:
            notice_user = NoticeUserModel.objects.get(id=notice_user_id, user_id=user_id)
            notice_user.mark_as_read()
            return True
        except NoticeUserModel.DoesNotExist:
            return False
    
    @staticmethod
    def mark_as_handled(notice_user_id: str, user_id: str) -> bool:
        """
        标记消息为已处理
        
        Args:
            notice_user_id: 用户消息关联ID
            user_id: 用户ID（用于验证权限）
            
        Returns:
            是否成功
        """
        try:
            notice_user = NoticeUserModel.objects.get(id=notice_user_id, user_id=user_id)
            notice_user.mark_as_handled()
            return True
        except NoticeUserModel.DoesNotExist:
            return False
    
    @staticmethod
    def mark_as_ignored(notice_user_id: str, user_id: str) -> bool:
        """
        标记消息为已忽略
        
        Args:
            notice_user_id: 用户消息关联ID
            user_id: 用户ID（用于验证权限）
            
        Returns:
            是否成功
        """
        try:
            notice_user = NoticeUserModel.objects.get(id=notice_user_id, user_id=user_id)
            notice_user.mark_as_ignored()
            return True
        except NoticeUserModel.DoesNotExist:
            return False
    
    @staticmethod
    def delete_notice(notice_user_id: str, user_id: str) -> bool:
        """
        删除消息（用户侧软删除）
        
        Args:
            notice_user_id: 用户消息关联ID
            user_id: 用户ID（用于验证权限）
            
        Returns:
            是否成功
        """
        try:
            notice_user = NoticeUserModel.objects.get(id=notice_user_id, user_id=user_id)
            notice_user.delete_mark = 1
            notice_user.save(update_fields=['delete_mark'])
            return True
        except NoticeUserModel.DoesNotExist:
            return False

