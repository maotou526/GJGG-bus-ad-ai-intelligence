"""
AI审核记录视图
Description: AI审核记录的CRUD操作和统计功能
Version: 1.0
Date: 2026-02-03
"""
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Count, Avg
from dvadmin.utils.viewset import CustomModelViewSet
from dvadmin.utils.json_response import DetailResponse, SuccessResponse, ErrorResponse
from dvadmin.utils.field_permission import FieldPermissionMixin
from dvadmin.system.models import FileList
from dvadmin.system.views.file_list import FileSerializer
from .models import AIAuditLogModel
from .serializers import (
    AIAuditLogSerializer,
    AIAuditLogCreateSerializer,
    AIAuditLogUpdateSerializer,
    AIAuditLogListSerializer,
    AIAuditLogDetailSerializer,
    AIAuditLogSimpleSerializer
)
from ..services import AIAuditService


class AIAuditLogViewSet(CustomModelViewSet, FieldPermissionMixin):
    """
    AI审核记录管理视图集

    功能说明：
    - 提供AI审核记录的增删改查功能
    - 支持按订单、材料、审核结果等条件筛选
    - 提供统计分析接口

    标准DRF接口：
    - GET /api/AIAuditLogViewSet/ - 获取审核记录列表
    - GET /api/AIAuditLogViewSet/{id}/ - 获取单个审核记录详情
    - POST /api/AIAuditLogViewSet/ - 创建审核记录
    - PUT /api/AIAuditLogViewSet/{id}/ - 更新审核记录
    - DELETE /api/AIAuditLogViewSet/{id}/ - 删除审核记录（软删除）

    自定义接口：
    - POST /api/AIAuditLogViewSet/upload_and_audit/ - 上传文件并触发AI审核
    - GET /api/AIAuditLogViewSet/statistics/ - 审核统计
    - GET /api/AIAuditLogViewSet/by_material/{material_id}/ - 获取材料的所有审核记录
    - GET /api/AIAuditLogViewSet/by_order/{order_id}/ - 获取订单的所有审核记录
    """

    # 查询集
    queryset = AIAuditLogModel.objects.all()

    # 支持文件上传
    parser_classes = (MultiPartParser, FormParser)

    # 默认序列化器
    serializer_class = AIAuditLogSerializer

    # 列表序列化器
    list_serializer_class = AIAuditLogListSerializer

    # 详情序列化器
    retrieve_serializer_class = AIAuditLogDetailSerializer

    # 创建序列化器
    create_serializer_class = AIAuditLogCreateSerializer

    # 更新序列化器
    update_serializer_class = AIAuditLogUpdateSerializer

    # 导出序列化器
    export_serializer_class = AIAuditLogListSerializer

    # 导出字段配置
    export_field_label = {
        'id': 'ID',
        'audit_no': '审核编号',
        'audit_source': '审核来源',
        'material_id': '材料ID',
        'order_id': '订单ID',
        'file_name': '文件名称',
        'audit_type': '审核类型',
        'platform': '调用平台',
        'request_time': '请求时间',
        'response_time': '响应时间',
        'duration_seconds': '耗时(秒)',
        'ai_conclusion': 'AI判定结果',
        'risk_level': '风险等级',
        'confidence_score': '置信度',
        'need_manual_review': '需人工复核',
        'error_message': '错误信息',
        'create_datetime': '创建时间',
        'creator_name': '创建人',
    }

    # 过滤字段
    filter_fields = [
        "id",
        "audit_no",
        "audit_source",
        "material_id",
        "order_id",
        "audit_type",
        "platform",
        "ai_conclusion",
        "risk_level",
        "need_manual_review",
        "delete_mark",
        "enabled_mark",
    ]

    # 搜索字段
    search_fields = ['audit_no', 'file_name', 'error_message']

    # 排序字段
    ordering_fields = [
        'id',
        'audit_no',
        'request_time',
        'response_time',
        'duration_seconds',
        'ai_conclusion',
        'risk_level',
        'confidence_score',
        'create_datetime',
    ]

    # 默认排序
    ordering = ['-create_datetime']

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def statistics(self, request):
        """
        审核统计
        """
        data = {
            'total': self.queryset.count(),
            'passed': self.queryset.filter(ai_conclusion=1).count(),
            'warning': self.queryset.filter(ai_conclusion=2).count(),
            'rejected': self.queryset.filter(ai_conclusion=3).count(),
            'failed': self.queryset.filter(ai_conclusion=4).count(),
        }
        return DetailResponse(data=data, msg="获取成功")

    @action(methods=['POST'], detail=False, permission_classes=[])
    def upload_and_audit(self, request):
        """
        上传文件并触发AI审核

        请求参数（FormData）：
        - file: 文件对象（必填）
        - audit_source: 审核来源（1:关联订单 2:独立审核）
        - audit_type: 审核类型（1:画面内容 2:证明文件 3:综合审核）
        - material_id: 关联材料ID（关联订单审核时必填）
        - order_id: 上刊订单ID（可选）
        - description: 备注说明（可选）

        返回：审核结果
        """
        try:
            # 1. 获取上传的文件
            file = request.FILES.get('file')
            if not file:
                return ErrorResponse(msg="请上传文件")

            # 2. 获取表单参数
            audit_source = int(request.data.get('audit_source', 2))
            audit_type = int(request.data.get('audit_type', 1))
            material_id = request.data.get('material_id') or None
            order_id = request.data.get('order_id') or None
            description = request.data.get('description', '')

            # 3. 验证关联订单审核时必须填写material_id
            if audit_source == 1 and not material_id:
                return ErrorResponse(msg="关联订单审核时必须填写关联材料ID")

            print(f"[上传审核] 收到文件: {file.name}, 大小: {file.size} bytes")
            print(f"[上传审核] 参数: audit_source={audit_source}, audit_type={audit_type}, material_id={material_id}")

            # 4. 保存文件到文件系统/OSS
            file_serializer = FileSerializer(
                data={'file': file},
                context={'request': request}
            )
            file_serializer.is_valid(raise_exception=True)
            file_obj = file_serializer.save()

            # 5. 构建文件路径和文件名（使用 file_obj 的属性）
            file_name = file_obj.name  # 使用文件对象的名称
            file_path = file_obj.file_url

            print(f"[上传审核] 文件已保存: ID={file_obj.id}, 文件名={file_name}, 路径={file_path}")

            # 6. 重置文件指针，准备传递给AI审核
            file.seek(0)

            # 7. 触发AI审核（直接传递内存中的 file 对象，避免磁盘IO）
            audit_service = AIAuditService()
            audit_result = audit_service.audit_file(
                file_id=str(file_obj.id),  # 转为字符串传递附件ID
                file_path=file_path,  # 使用 file_obj 构建的文件路径
                file_name=file_name,  # 使用 file_obj 的文件名
                file_object=file,  # 传递内存中的文件对象（优先使用）
                audit_type=audit_type,
                material_id=material_id,
                order_id=order_id,
                audit_source=audit_source,
                description=description
            )

            print(f"[上传审核] 审核完成: {audit_result.get('audit_no')}, 结果: {audit_result.get('ai_conclusion')}")

            return DetailResponse(data=audit_result, msg="审核完成")

        except ValueError as e:
            print(f"[上传审核] 参数错误: {str(e)}")
            return ErrorResponse(msg=f"参数错误: {str(e)}")
        except Exception as e:
            print(f"[上传审核] 审核失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return ErrorResponse(msg=f"审核失败: {str(e)}", code=5000)