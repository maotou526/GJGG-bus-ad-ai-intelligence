'''
Description: 环域信息视图集
Version: 1.0
Author: CursorAgent
Date: 2025-11-10 00:00:00
LastEditors: CursorAgent
LastEditTime: 2025-11-10 00:00:00
'''
from django.db.models import Avg, Count
from rest_framework.decorators import action

from dvadmin.utils.json_response import SuccessResponse
from dvadmin.utils.viewset import CustomModelViewSet

from .models import DcBaseTorusinfoModel
from .serializers import (
    DcBaseTorusinfoSerializer,
    DcBaseTorusinfoCreateSerializer,
    DcBaseTorusinfoUpdateSerializer,
    DcBaseTorusinfoListSerializer,
    DcBaseTorusinfoExportSerializer,
)


class DcBaseTorusinfoModelViewSet(CustomModelViewSet):
    """
    环域信息模型视图集
    提供标准的 CRUD 接口及统计接口
    """

    queryset = DcBaseTorusinfoModel.objects.all()
    serializer_class = DcBaseTorusinfoSerializer
    create_serializer_class = DcBaseTorusinfoCreateSerializer
    update_serializer_class = DcBaseTorusinfoUpdateSerializer
    list_serializer_class = DcBaseTorusinfoListSerializer
    export_serializer_class = DcBaseTorusinfoExportSerializer
    ordering_fields = ["id", "torus", "create_date", "modify_date"]
    ordering = ["-create_date"]

    @action(detail=False, methods=["get"], url_path="summary")
    def get_summary(self, request):
        """
        获取环域信息统计
        包含总数以及平均环域值
        """
        queryset = self.get_queryset()
        stats = queryset.aggregate(
            total_count=Count("id"),
            average_torus=Avg("torus"),
        )
        return SuccessResponse(
            data={
                "total": stats.get("total_count", 0) or 0,
                "average_torus": round(stats.get("average_torus") or 0, 2) if stats.get("average_torus") else None,
            },
            msg="获取统计信息成功",
        )
