"""
AI审核反馈视图
Description: AI审核反馈的CRUD操作和统计功能
Version: 1.0
Date: 2026-02-03
"""
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Avg
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from dvadmin.utils.field_permission import FieldPermissionMixin
from .models import AIAuditFeedbackModel
from .serializers import (
    AIAuditFeedbackSerializer,
    AIAuditFeedbackCreateSerializer,
    AIAuditFeedbackUpdateSerializer,
    AIAuditFeedbackListSerializer,
    AIAuditFeedbackDetailSerializer
)


class AIAuditFeedbackViewSet(CustomModelViewSet, FieldPermissionMixin):
    """
    AI审核反馈管理视图集

    功能说明：
    - 提供AI审核反馈的增删改查功能
    - 支持按审核记录、审核员等条件筛选
    - 提供反馈统计和AI准确性分析接口

    标准DRF接口：
    - GET /api/AIAuditFeedbackViewSet/ - 获取反馈列表
    - GET /api/AIAuditFeedbackViewSet/{id}/ - 获取单个反馈详情
    - POST /api/AIAuditFeedbackViewSet/ - 创建反馈
    - PUT /api/AIAuditFeedbackViewSet/{id}/ - 更新反馈
    - DELETE /api/AIAuditFeedbackViewSet/{id}/ - 删除反馈

    自定义接口：
    - GET /api/AIAuditFeedbackViewSet/statistics/ - 反馈统计
    - GET /api/AIAuditFeedbackViewSet/accuracy_analysis/ - AI准确性分析
    - GET /api/AIAuditFeedbackViewSet/by_audit_log/{audit_log_id}/ - 获取审核记录的反馈
    """

    # 查询集
    queryset = AIAuditFeedbackModel.objects.all()

    # 默认序列化器
    serializer_class = AIAuditFeedbackSerializer

    # 列表序列化器
    list_serializer_class = AIAuditFeedbackListSerializer

    # 详情序列化器
    retrieve_serializer_class = AIAuditFeedbackDetailSerializer

    # 创建序列化器
    create_serializer_class = AIAuditFeedbackCreateSerializer

    # 更新序列化器
    update_serializer_class = AIAuditFeedbackUpdateSerializer

    # 导出序列化器
    export_serializer_class = AIAuditFeedbackListSerializer

    # 导出字段配置
    export_field_label = {
        'id': 'ID',
        'audit_log_id': '审核记录ID',
        'reviewer_id': '审核员ID',
        'reviewer_name': '审核员姓名',
        'manual_conclusion': '人工判定结果',
        'final_result': '最终审核结果',
        'ai_accuracy': 'AI判定准确性',
        'feedback_text': '反馈说明',
        'feedback_time': '反馈时间',
        'create_datetime': '创建时间',
        'creator_name': '创建人',
    }

    # 过滤字段
    filter_fields = [
        "id",
        "audit_log_id",
        "reviewer_id",
        "manual_conclusion",
        "final_result",
        "ai_accuracy",
        "delete_mark",
        "enabled_mark",
    ]

    # 搜索字段
    search_fields = ['reviewer_name', 'feedback_text']

    # 排序字段
    ordering_fields = [
        'id',
        'audit_log_id',
        'reviewer_id',
        'manual_conclusion',
        'final_result',
        'ai_accuracy',
        'feedback_time',
        'create_datetime',
    ]

    # 默认排序
    ordering = ['-feedback_time']
