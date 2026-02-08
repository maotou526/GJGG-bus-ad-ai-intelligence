'''
Description: 环域信息序列化器
Version: 1.0
Author: CursorAgent
Date: 2025-11-10 00:00:00
LastEditors: CursorAgent
LastEditTime: 2025-11-10 00:00:00
'''
from rest_framework import serializers

from dvadmin.utils.serializers import CustomModelSerializer

from .models import DcBaseTorusinfoModel


class DcBaseTorusinfoSerializer(CustomModelSerializer):
    """
    环域信息序列化器
    用于通用的序列化与反序列化
    """

    class Meta:
        model = DcBaseTorusinfoModel
        fields = [
            "id",
            "explain",
            "torus",
            "remarks",
            "delete_mark",
            "enabled_mark",
            "create_date",
            "create_user_id",
            "create_user_name",
            "modify_date",
            "modify_user_id",
            "modify_user_name",
        ]
        read_only_fields = [
            "create_date",
            "create_user_id",
            "create_user_name",
            "modify_date",
            "modify_user_id",
            "modify_user_name",
        ]
        extra_kwargs = {
            "id": {
                "required": True,
                "allow_blank": False,
                "help_text": "主键ID"
            },
            "explain": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
                "help_text": "说明"
            },
            "torus": {
                "required": False,
                "allow_null": True,
                "help_text": "环域"
            },
            "remarks": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
                "help_text": "备注"
            },
            "delete_mark": {
                "required": False,
                "allow_null": True,
                "help_text": "删除标识，0表示未删除，1表示已删除"
            },
            "enabled_mark": {
                "required": False,
                "allow_null": True,
                "help_text": "是否禁用，0表示禁用，1表示启用"
            },
        }

    def validate_id(self, value):
        """
        验证主键 ID
        """
        if not value or not value.strip():
            raise serializers.ValidationError("主键ID不能为空")
        if len(value) > 50:
            raise serializers.ValidationError("主键ID长度不能超过50个字符")
        return value.strip()

    def validate_explain(self, value):
        """
        验证说明字段
        """
        if value and len(value) > 500:
            raise serializers.ValidationError("说明长度不能超过500个字符")
        return value

    def validate_remarks(self, value):
        """
        验证备注字段
        """
        if value and len(value) > 500:
            raise serializers.ValidationError("备注长度不能超过500个字符")
        return value


class DcBaseTorusinfoCreateSerializer(DcBaseTorusinfoSerializer):
    """
    环域信息创建序列化器
    """

    class Meta(DcBaseTorusinfoSerializer.Meta):
        pass


class DcBaseTorusinfoUpdateSerializer(DcBaseTorusinfoSerializer):
    """
    环域信息更新序列化器
    更新操作允许部分字段为空
    """

    class Meta(DcBaseTorusinfoSerializer.Meta):
        extra_kwargs = DcBaseTorusinfoSerializer.Meta.extra_kwargs.copy()
        extra_kwargs["id"]["required"] = False


class DcBaseTorusinfoListSerializer(DcBaseTorusinfoSerializer):
    """
    环域信息列表序列化器
    """

    class Meta(DcBaseTorusinfoSerializer.Meta):
        fields = [
            "id",
            "explain",
            "torus",
            "remarks",
            "delete_mark",
            "enabled_mark",
            "create_date",
            "create_user_name",
            "modify_date",
            "modify_user_name",
        ]
        read_only_fields = fields


class DcBaseTorusinfoExportSerializer(DcBaseTorusinfoListSerializer):
    """
    环域信息导出序列化器
    """

    class Meta(DcBaseTorusinfoListSerializer.Meta):
        fields = [
            "id",
            "explain",
            "torus",
            "remarks",
            "create_date",
            "modify_date",
        ]

