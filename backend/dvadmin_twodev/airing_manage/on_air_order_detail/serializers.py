"""
Description: 上刊订单明细序列化器
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import OnAirOrderDetailModel


class OnAirOrderDetailModelSerializer(CustomModelSerializer):
    """
    上刊订单明细序列化器

    功能说明:
    - 提供上刊订单明细数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer, 获得审计字段自动填充功能
    """

    # 执行状态显示名称
    execution_status_display = serializers.SerializerMethodField()

    class Meta:
        model = OnAirOrderDetailModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "order_id": {"required": True, "allow_null": False},
            "position_id": {"required": True, "allow_null": False},
            "roadline_id": {"required": True, "allow_null": False},
            "roadline_name": {"required": False, "allow_null": True, "allow_blank": True},
            "roadline_company_id": {"required": True, "allow_null": False},
            "roadline_company_name": {"required": False, "allow_null": True, "allow_blank": True},
            "plan_vehicle_id": {"required": False, "allow_null": True},
            "plan_vehicle_no": {"required": False, "allow_null": True, "allow_blank": True},
            "act_vehicle_id": {"required": False, "allow_null": True},
            "act_vehicle_no": {"required": False, "allow_null": True, "allow_blank": True},
            "composite_media_type_id": {"required": False, "allow_null": True},
            "composite_media_type_name": {"required": False, "allow_null": True, "allow_blank": True},
            "base_media_type_id": {"required": True, "allow_null": False},
            "base_media_type_name": {"required": False, "allow_null": True, "allow_blank": True},
            "act_on_air_datetime": {"required": False, "allow_null": True, "format": "%Y-%m-%d %H:%M:%S", "input_formats": ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]},
            "execution_status": {"required": True, "allow_null": False},
            "remark": {"required": False, "allow_null": True, "allow_blank": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_execution_status_display(self, obj):
        """执行状态显示名称"""
        status_map = {
            1: "待执行",
            2: "施工中",
            3: "已完成",
        }
        return status_map.get(obj.execution_status, "未知")

    def validate_execution_status(self, value):
        """验证执行状态"""
        if value not in [1, 2, 3]:
            raise serializers.ValidationError("执行状态只能是：1=待执行, 2=施工中, 3=已完成")
        return value

    def validate(self, attrs):
        """整体验证"""
        # 如果实际上刊车辆与预订车辆不同，可以在这里添加业务逻辑验证
        plan_vehicle_id = attrs.get("plan_vehicle_id")
        act_vehicle_id = attrs.get("act_vehicle_id")
        
        # 如果填写了实际上刊车辆，但没有填写实际上刊时间，可以给出提示
        if act_vehicle_id and not attrs.get("act_on_air_datetime"):
            # 这里不强制要求，因为可能是在施工中状态
            pass
        
        return attrs


class OnAirOrderDetailModelCreateSerializer(OnAirOrderDetailModelSerializer):
    """
    上刊订单明细创建序列化器

    功能说明:
    - 专门用于创建新上刊订单明细时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(OnAirOrderDetailModelSerializer.Meta):
        extra_kwargs = {
            **OnAirOrderDetailModelSerializer.Meta.extra_kwargs,
            "order_id": {"required": True, "allow_null": False},
            "position_id": {"required": True, "allow_null": False},
            "roadline_id": {"required": True, "allow_null": False},
            "roadline_company_id": {"required": True, "allow_null": False},
            "base_media_type_id": {"required": True, "allow_null": False},
            "execution_status": {"required": True, "allow_null": False},
        }

    def create(self, validated_data):
        """创建上刊订单明细时自动填充部分冗余字段"""
        # 从关联对象自动填充冗余字段
        position_id = validated_data.get("position_id")
        if position_id:
            try:
                # 从车位广告获取线路信息
                if hasattr(position_id, "roadline_id"):
                    if not validated_data.get("roadline_name") and hasattr(position_id.roadline_id, "line_name"):
                        validated_data["roadline_name"] = position_id.roadline_id.line_name
                
                # 从车位广告获取公司信息
                if hasattr(position_id, "roadline_company_id"):
                    if not validated_data.get("roadline_company_name") and hasattr(position_id.roadline_company_id, "company_name"):
                        validated_data["roadline_company_name"] = position_id.roadline_company_id.company_name
                
                # 从车位广告获取车辆信息
                if hasattr(position_id, "vehicle_id") and position_id.vehicle_id:
                    if not validated_data.get("plan_vehicle_id"):
                        validated_data["plan_vehicle_id"] = position_id.vehicle_id
                    if not validated_data.get("plan_vehicle_no") and hasattr(position_id.vehicle_id, "vehicle_no"):
                        validated_data["plan_vehicle_no"] = position_id.vehicle_id.vehicle_no
            except Exception:
                pass

        # 从基础媒体类型获取名称
        base_media_type_id = validated_data.get("base_media_type_id")
        if base_media_type_id and not validated_data.get("base_media_type_name"):
            try:
                if hasattr(base_media_type_id, "media_name"):
                    validated_data["base_media_type_name"] = base_media_type_id.media_name
            except Exception:
                pass

        # 从组合媒体类型获取名称
        composite_media_type_id = validated_data.get("composite_media_type_id")
        if composite_media_type_id and not validated_data.get("composite_media_type_name"):
            try:
                if hasattr(composite_media_type_id, "media_name"):
                    validated_data["composite_media_type_name"] = composite_media_type_id.media_name
            except Exception:
                pass

        return super().create(validated_data)


class OnAirOrderDetailModelUpdateSerializer(OnAirOrderDetailModelSerializer):
    """
    上刊订单明细更新序列化器

    功能说明:
    - 专门用于更新现有上刊订单明细时的数据验证
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(OnAirOrderDetailModelSerializer.Meta):
        read_only_fields = ["id", "create_datetime", "update_datetime", "order_id", "position_id"]

    def update(self, instance, validated_data):
        """更新时自动填充部分冗余字段"""
        # 如果更新了实际上刊车辆，自动填充车辆自编号
        act_vehicle_id = validated_data.get("act_vehicle_id")
        if act_vehicle_id and act_vehicle_id != instance.act_vehicle_id:
            try:
                if hasattr(act_vehicle_id, "vehicle_no") and not validated_data.get("act_vehicle_no"):
                    validated_data["act_vehicle_no"] = act_vehicle_id.vehicle_no
            except Exception:
                pass

        return super().update(instance, validated_data)


class OnAirOrderDetailModelListSerializer(OnAirOrderDetailModelSerializer):
    """
    上刊订单明细列表序列化器

    功能说明:
    - 专门用于上刊订单明细列表显示, 优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量, 提高响应速度
    - 所有字段为只读, 确保数据安全
    """

    class Meta:
        model = OnAirOrderDetailModel
        fields = [
            # 基础信息
            "id",
            "order_id",
            "position_id",
            # 线路与公司
            "roadline_id",
            "roadline_name",
            "roadline_company_id",
            "roadline_company_name",
            # 车辆信息
            "plan_vehicle_id",
            "plan_vehicle_no",
            "act_vehicle_id",
            "act_vehicle_no",
            # 媒体类型
            "composite_media_type_id",
            "composite_media_type_name",
            "base_media_type_id",
            "base_media_type_name",
            # 时间信息
            "act_on_air_datetime",
            # 状态信息
            "execution_status",
            "execution_status_display",
            # 备注
            "remark",
            # 审计字段
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
            "enabled_mark",
            "delete_mark",
        ]
        read_only_fields = fields
