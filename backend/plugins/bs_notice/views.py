'''
Description: 消息通知视图
Version: 1.0
Autor: AI Assistant
Date: 2026-02-05
LastEditors: 
LastEditTime: 2026-02-05
'''
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from .models import NoticeModel, NoticeUserModel
from .serializers import (
    NoticeModelSerializer,
    NoticeModelCreateSerializer,
    NoticeModelUpdateSerializer,
    NoticeModelListSerializer,
    NoticeUserModelSerializer,
    NoticeUserModelCreateSerializer,
    NoticeUserModelUpdateSerializer,
    NoticeUserModelListSerializer,
)
from .services import NoticeService
from .constants import NoticeTemplate
from django.db.models import Q
from django.utils import timezone


class NoticeModelViewSet(CustomModelViewSet):
    """
    消息主表视图集
    
    功能说明:
    - 提供消息的增删改查功能(使用DRF标准接口)
    - 自动处理分页、过滤、排序等功能
    - 支持批量删除和启用/禁用操作
    
    标准DRF接口:
    - GET /api/bs_notice/notice/ - 获取消息列表
    - POST /api/bs_notice/notice/ - 创建消息
    - PUT /api/bs_notice/notice/{id}/ - 更新消息
    - DELETE /api/bs_notice/notice/{id}/ - 删除消息
    """
    permission_classes = [IsAuthenticated]
    
    # 查询集
    queryset = NoticeModel.objects.all()
    
    # 默认序列化器(用于查询详情)
    serializer_class = NoticeModelSerializer
    
    # 列表序列化器(用于列表展示)
    list_serializer_class = NoticeModelListSerializer
    
    # 创建序列化器
    create_serializer_class = NoticeModelCreateSerializer
    
    # 更新序列化器
    update_serializer_class = NoticeModelUpdateSerializer
    
    # 过滤字段(支持精确查询)
    filter_fields = [
        'id', 'msg_type', 'rec_table', 'rec_id', 'priority', 'send_type',
        'sender_id', 'enabled_mark', 'delete_mark'
    ]
    
    # filterset_fields 用于 DRF 的过滤后端
    filterset_fields = [
        'id', 'msg_type', 'rec_table', 'rec_id', 'priority', 'send_type',
        'sender_id', 'enabled_mark', 'delete_mark'
    ]
    
    # 搜索字段(支持模糊查询)
    search_fields = ['title', 'content', 'sender_name']
    
    def get_queryset(self):
        """过滤过期消息"""
        queryset = super().get_queryset()
        # 默认过滤过期消息
        if self.request.query_params.get('include_expired', '0') != '1':
            queryset = queryset.filter(
                Q(expire_time__isnull=True) | Q(expire_time__gt=timezone.now())
            )
        return queryset
    
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def send_notification(self, request):
        """
        发送消息（使用服务类）
        """
        try:
            notice = NoticeService.send_notification(
                msg_type=request.data.get('msg_type'),
                title=request.data.get('title'),
                content=request.data.get('content'),
                jump_url=request.data.get('jump_url'),
                priority=request.data.get('priority', 2),
                send_type=request.data.get('send_type', 1),
                sender_id=request.data.get('sender_id'),
                sender_name=request.data.get('sender_name'),
                rec_table=request.data.get('rec_table'),
                rec_id=request.data.get('rec_id'),
                extra_data=request.data.get('extra_data'),
                expire_time=request.data.get('expire_time'),
                request=request
            )
            return SuccessResponse(data=NoticeModelSerializer(notice).data, msg="消息发送成功")
        except Exception as e:
            return ErrorResponse(msg=f"消息发送失败：{str(e)}")
    
    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def send_by_template(self, request):
        """
        使用模板发送消息
        """
        try:
            template_code = request.data.get('template_code')
            if not template_code:
                return ErrorResponse(msg="模板编码不能为空")
            
            # 获取模板
            template = getattr(NoticeTemplate, template_code.upper(), None)
            if not template:
                return ErrorResponse(msg=f"模板 {template_code} 不存在")
            
            notice = NoticeService.send_by_template(
                template=template,
                rec_table=request.data.get('rec_table'),
                rec_id=request.data.get('rec_id'),
                send_type=request.data.get('send_type', 1),
                extra_data=request.data.get('extra_data'),
                variables=request.data.get('variables', {}),
                sender_id=request.data.get('sender_id'),
                sender_name=request.data.get('sender_name'),
                expire_time=request.data.get('expire_time'),
                request=request
            )
            return SuccessResponse(data=NoticeModelSerializer(notice).data, msg="消息发送成功")
        except Exception as e:
            return ErrorResponse(msg=f"消息发送失败：{str(e)}")


class NoticeUserModelViewSet(CustomModelViewSet):
    """
    用户消息关联视图集
    
    功能说明:
    - 提供用户消息的查询、标记已读、处理等功能
    - 支持查询当前用户的消息列表
    
    标准DRF接口:
    - GET /api/bs_notice/notice_user/ - 获取用户消息列表
    - GET /api/bs_notice/notice_user/{id}/ - 获取消息详情
    """
    permission_classes = [IsAuthenticated]
    
    # 查询集
    queryset = NoticeUserModel.objects.all()
    
    # 默认序列化器(用于查询详情)
    serializer_class = NoticeUserModelSerializer
    
    # 列表序列化器(用于列表展示)
    list_serializer_class = NoticeUserModelListSerializer
    
    # 创建序列化器
    create_serializer_class = NoticeUserModelCreateSerializer
    
    # 更新序列化器
    update_serializer_class = NoticeUserModelUpdateSerializer
    
    # 过滤字段
    filter_fields = [
        'id', 'notice_id', 'user_id', 'user_name', 'read_status', 'handle_status', 'delete_mark'
    ]

    filterset_fields = [
        'id', 'notice_id', 'user_id', 'user_name', 'read_status', 'handle_status', 'delete_mark'
    ]

    # 搜索字段（模糊匹配，通过 ?search=xxx 触发）
    search_fields = ['user_name']
    
    # def get_queryset(self):
    #     """只返回当前用户的消息"""
    #     queryset = super().get_queryset()
    #     user_id = str(self.request.user.id)
    #     queryset = queryset.filter(user_id=user_id, is_deleted=False)
        
    #     # 获取消息ID列表
    #     notice_ids = list(queryset.values_list('notice_id', flat=True))
        
    #     if notice_ids:
    #         # 过滤过期消息
    #         from .models import NoticeModel
    #         valid_notices = NoticeModel.objects.filter(
    #             id__in=notice_ids
    #         ).filter(
    #             Q(expire_time__isnull=True) | Q(expire_time__gt=timezone.now())
    #         ).values_list('id', flat=True)
            
    #         # 只返回有效消息的用户记录
    #         queryset = queryset.filter(notice_id__in=valid_notices)
        
    #     return queryset
    
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def unread_count(self, request):
        """
        获取当前用户未读消息数量
        """
        user_id = str(request.user.id)
        count = NoticeService.get_unread_count(user_id)
        return SuccessResponse(data={"count": count}, msg="获取成功")
    
    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def my_notices(self, request):
        """
        获取当前用户的消息列表
        """
        user_id = str(request.user.id)
        msg_type = request.query_params.get('msg_type')
        read_status = request.query_params.get('read_status')
        handle_status = request.query_params.get('handle_status')
        limit = int(request.query_params.get('limit', 20))
        offset = int(request.query_params.get('offset', 0))
        
        # 获取总数（先查询总数，避免重复查询）
        from .models import NoticeUserModel, NoticeModel
        from django.db.models import Q
        from django.utils import timezone
        
        notice_user_queryset = NoticeUserModel.objects.filter(
            user_id=user_id,
            delete_mark=0
        )
        
        if read_status is not None:
            notice_user_queryset = notice_user_queryset.filter(read_status=int(read_status))
        
        if handle_status is not None:
            notice_user_queryset = notice_user_queryset.filter(handle_status=int(handle_status))
        
        notice_ids = list(notice_user_queryset.values_list('notice_id', flat=True))
        
        if notice_ids:
            notice_queryset = NoticeModel.objects.filter(id__in=notice_ids)
            notice_queryset = notice_queryset.filter(
                Q(expire_time__isnull=True) | Q(expire_time__gt=timezone.now())
            )
            
            if msg_type is not None:
                notice_queryset = notice_queryset.filter(msg_type=int(msg_type))
            
            total = notice_queryset.count()
        else:
            total = 0
        
        # 获取分页数据
        notices = NoticeService.get_user_notices(
            user_id=user_id,
            msg_type=int(msg_type) if msg_type else None,
            read_status=int(read_status) if read_status else None,
            handle_status=int(handle_status) if handle_status else None,
            limit=limit,
            offset=offset
        )
        
        # 计算当前页
        current_page = (offset // limit) + 1 if limit > 0 else 1
        
        return SuccessResponse(
            data=notices if isinstance(notices, list) else [],
            msg="获取成功",
            page=current_page,
            limit=limit,
            total=total
        )
    
    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def mark_read(self, request, pk=None):
        """
        标记消息为已读
        """
        try:
            instance = NoticeUserModel.objects.get(id=pk)
            instance.mark_as_read()
            return SuccessResponse(msg="标记成功")
        except NoticeUserModel.DoesNotExist:
            return ErrorResponse(msg="消息不存在")

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def mark_handled(self, request, pk=None):
        """
        标记消息为已处理
        """
        try:
            instance = NoticeUserModel.objects.get(id=pk)
            instance.mark_as_handled()
            return SuccessResponse(msg="标记成功")
        except NoticeUserModel.DoesNotExist:
            return ErrorResponse(msg="消息不存在")

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def mark_ignored(self, request, pk=None):
        """
        标记消息为已忽略
        """
        try:
            instance = NoticeUserModel.objects.get(id=pk)
            instance.mark_as_ignored()
            return SuccessResponse(msg="标记成功")
        except NoticeUserModel.DoesNotExist:
            return ErrorResponse(msg="消息不存在")

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated])
    def delete_notice(self, request, pk=None):
        """
        删除消息（用户侧软删除）
        """
        try:
            instance = NoticeUserModel.objects.get(id=pk)
            instance.delete_mark = 1
            instance.save(update_fields=['delete_mark'])
            return SuccessResponse(msg="删除成功")
        except NoticeUserModel.DoesNotExist:
            return ErrorResponse(msg="消息不存在")

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def batch_mark_read(self, request):
        """
        批量标记为已读
        """
        notice_user_ids = request.data.get('ids', [])
        instances = NoticeUserModel.objects.filter(id__in=notice_user_ids)
        success_count = 0
        for instance in instances:
            instance.mark_as_read()
            success_count += 1
        return SuccessResponse(data={"success_count": success_count}, msg=f"成功标记 {success_count} 条消息")

    @action(methods=['POST'], detail=False, permission_classes=[IsAuthenticated])
    def batch_delete(self, request):
        """
        批量删除消息
        """
        notice_user_ids = request.data.get('ids', [])
        success_count = NoticeUserModel.objects.filter(id__in=notice_user_ids).update(delete_mark=1)
        return SuccessResponse(data={"success_count": success_count}, msg=f"成功删除 {success_count} 条消息")

