"""
Description: 基础日期管理序列化器
Version: 1.0
Autor: 王晨
Date: 2025-10-23
LastEditors: 王晨
LastEditTime: 2025-10-23
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import BaseDateModel


class BaseDateModelSerializer(CustomModelSerializer):
    """
    基础日期管理序列化器
    """
    
    date_type_display = serializers.SerializerMethodField()
    week_display = serializers.SerializerMethodField()

    class Meta:
        model = BaseDateModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "date": {"required": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "month": {"required": False, "allow_null": True},
            "count": {"required": False, "allow_null": True},
            "date_type": {"required": False, "allow_null": True},
            "name": {"required": False, "allow_null": True, "allow_blank": True},
            "week": {"required": False, "allow_null": True},
            "is_work": {"required": False},
        }

    def get_date_type_display(self, obj):
        """日期类型显示名称"""
        type_map = {
            0: "工作日",
            1: "休息日",
        }
        return type_map.get(obj.date_type, "未知")

    def get_week_display(self, obj):
        """星期显示名称"""
        week_map = {
            0: "星期日",
            1: "星期一",
            2: "星期二",
            3: "星期三",
            4: "星期四",
            5: "星期五",
            6: "星期六"
        }
        return week_map.get(obj.week, "未知") if obj.week is not None else None

    def validate_date_type(self, value):
        """验证日期类型"""
        if value is not None and value not in [0, 1]:
            raise serializers.ValidationError("日期类型只能是0(工作日)或1(休息日)")
        return value

    def validate_week(self, value):
        """验证星期"""
        if value is not None and not (0 <= value <= 6):
            raise serializers.ValidationError("星期只能是0-6(0为星期日，1为星期一)")
        return value

    def validate_month(self, value):
        """验证月份"""
        if value is not None and not (1 <= value <= 12):
            raise serializers.ValidationError("月份只能是1-12")
        return value

    def validate_count(self, value):
        """验证当月天数"""
        if value is not None and not (28 <= value <= 31):
            raise serializers.ValidationError("当月天数只能是28-31")
        return value


class BaseDateModelListSerializer(BaseDateModelSerializer):
    """
    基础日期列表序列化器
    """

    class Meta:
        model = BaseDateModel
        fields = [
            "id",
            "date",
            "month",
            "count",
            "date_type",
            "date_type_display",
            "name",
            "week",
            "week_display",
            "is_work",
            "create_datetime",
            "update_datetime",
        ]
        read_only_fields = fields


class BaseDateModelImportSerializer(CustomModelSerializer):
    """
    基础日期导入序列化器
    """
    
    class Meta:
        model = BaseDateModel
        fields = [
            'date',
            'month',
            'date_type',
            'name',
            'is_work',
        ]
        extra_kwargs = {
            'date': {'required': True},
            'month': {'required': False, 'allow_null': True},
            'date_type': {'required': False, 'allow_null': True},
            'name': {'required': False, 'allow_null': True, 'allow_blank': True},
            'is_work': {'required': False},
        }
    
    def validate_date_type(self, value):
        """验证日期类型"""
        if value is not None and value not in [0, 1]:
            raise serializers.ValidationError("日期类型只能是0(工作日)或1(休息日)")
        return value

