"""
Description: 上刊材料序列化器
Version: 1.0
Autor: AI Assistant
Date: 2026-03-17
LastEditors:
LastEditTime: 2026-03-17
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import OnAirMaterialModel


class OnAirMaterialModelSerializer(CustomModelSerializer):
    """
    上刊材料序列化器

    功能说明:
    - 提供上刊材料数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer, 获得审计字段自动填充功能
    """

    # 材料类别显示名称
    material_category_display = serializers.SerializerMethodField()

    # 审核状态显示名称
    audit_status_display = serializers.SerializerMethodField()

    class Meta:
        model = OnAirMaterialModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "order_id": {"required": True, "allow_null": False},
            "material_category": {"required": True, "allow_null": False},
            "material_type_code": {"required": False, "allow_null": True, "allow_blank": True},
            "material_type_name": {"required": True, "allow_null": False, "allow_blank": False},
            "file_name": {"required": True, "allow_null": False, "allow_blank": False},
            "file_path": {"required": True, "allow_null": False, "allow_blank": False},
            "file_size": {"required": False, "allow_null": True},
            "file_format": {"required": False, "allow_null": True, "allow_blank": True},
            "is_required": {"required": False, "allow_null": True},
            "audit_status": {"required": False, "allow_null": True},
            "latest_ai_audit_id": {"required": False, "allow_null": True, "allow_blank": True},
            "uploader_id": {"required": False, "allow_null": True, "allow_blank": True},
            "upload_time": {"required": True, "allow_null": False, "format": "%Y-%m-%d %H:%M:%S", "input_formats": ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]},
            "remark": {"required": False, "allow_null": True, "allow_blank": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_material_category_display(self, obj):
        """材料类别显示名称"""
        category_map = {
            1: "广告画面",
            2: "合规证明",
            3: "施工方案",
            4: "其他",
        }
        return category_map.get(obj.material_category, "未知")

    def get_audit_status_display(self, obj):
        """审核状态显示名称"""
        status_map = {
            10: "待AI审核",
            11: "AI审核中",
            20: "待人工复核",
            30: "已通过",
            40: "已驳回",
        }
        return status_map.get(obj.audit_status, "未知")


class OnAirMaterialModelCreateSerializer(OnAirMaterialModelSerializer):
    """
    上刊材料创建序列化器

    功能说明:
    - 专门用于创建新上刊材料时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(OnAirMaterialModelSerializer.Meta):
        extra_kwargs = {
            **OnAirMaterialModelSerializer.Meta.extra_kwargs,
            "order_id": {"required": True, "allow_null": False},
            "material_category": {"required": True, "allow_null": False},
            "material_type_name": {"required": True, "allow_null": False, "allow_blank": False},
            "file_name": {"required": True, "allow_null": False, "allow_blank": False},
            "file_path": {"required": True, "allow_null": False, "allow_blank": False},
            "upload_time": {"required": True, "allow_null": False},
        }


class OnAirMaterialModelUpdateSerializer(OnAirMaterialModelSerializer):
    """
    上刊材料更新序列化器

    功能说明:
    - 专门用于更新现有上刊材料时的数据验证
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(OnAirMaterialModelSerializer.Meta):
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OnAirMaterialModelListSerializer(OnAirMaterialModelSerializer):
    """
    上刊材料列表序列化器

    功能说明:
    - 专门用于上刊材料列表显示, 优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量, 提高响应速度
    - 所有字段为只读, 确保数据安全
    """

    class Meta:
        model = OnAirMaterialModel
        fields = [
            "id",
            "order_id",
            "material_category",
            "material_category_display",
            "material_type_code",
            "material_type_name",
            "file_name",
            "file_path",
            "file_size",
            "file_format",
            "is_required",
            "audit_status",
            "audit_status_display",
            "latest_ai_audit_id",
            "uploader_id",
            "upload_time",
            "remark",
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
            "enabled_mark",
            "delete_mark",
        ]
        read_only_fields = fields
