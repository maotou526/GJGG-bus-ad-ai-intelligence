"""
Description: 车型序列化器
"""
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import VehicleTypeModel


class VehicleTypeModelSerializer(CustomModelSerializer):
    """车型序列化器"""

    class Meta:
        model = VehicleTypeModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "company_code": {"required": False, "allow_null": True, "allow_blank": True},
            "company_name": {"required": False, "allow_null": True, "allow_blank": True},
            "vehicle_model_code": {"required": False, "allow_null": True, "allow_blank": True},
            "vehicle_model_name": {"required": False, "allow_null": True, "allow_blank": True},
            "rated_passenger_capacity": {"required": False, "allow_null": True},
            "is_purchased_model": {"required": False, "allow_null": True},
            "description": {"required": False, "allow_null": True, "allow_blank": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def validate_rated_passenger_capacity(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("额定载客量不能为负数")
        return value

    def validate_is_purchased_model(self, value):
        if value is not None and value not in [0, 1]:
            raise serializers.ValidationError("是否已购车型只能是0或1")
        return value


class VehicleTypeModelCreateSerializer(VehicleTypeModelSerializer):
    """创建序列化器"""

    class Meta(VehicleTypeModelSerializer.Meta):
        extra_kwargs = {
            **VehicleTypeModelSerializer.Meta.extra_kwargs,
            "vehicle_model_name": {"required": True},
        }


class VehicleTypeModelUpdateSerializer(VehicleTypeModelSerializer):
    """更新序列化器"""

    class Meta(VehicleTypeModelSerializer.Meta):
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class VehicleTypeModelListSerializer(VehicleTypeModelSerializer):
    """列表序列化器"""

    class Meta(VehicleTypeModelSerializer.Meta):
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]

