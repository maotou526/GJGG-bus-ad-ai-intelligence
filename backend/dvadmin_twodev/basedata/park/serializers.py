"""
Description: 停车场站序列化器
Version: 1.0
Autor: 王晨
Date: 2025-10-18
LastEditors: 王晨
LastEditTime: 2025-10-18
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import ParkModel


class ParkModelSerializer(CustomModelSerializer):
    """
    停车场站序列化器

    功能说明:
    - 提供场站数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 自动计算显示字段(如状态、类型名称等)
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer,获得审计字段自动填充功能
    """

    # 计算字段 - 场地类型显示名称
    park_type_display = serializers.SerializerMethodField()

    # 计算字段 - 场站类型显示名称
    station_type_display = serializers.SerializerMethodField()

    # 计算字段 - 停车场状态显示名称
    park_status_display = serializers.SerializerMethodField()

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()

    class Meta:
        model = ParkModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            # 整数字段类型配置
            "park_type": {"required": False, "allow_null": True},
            "station_type": {"required": False, "allow_null": True},
            "park_status": {"required": False, "allow_null": True},
            "repair_flag": {"required": False, "allow_null": True},
            "report_flag": {"required": False, "allow_null": True},
            "parking_space": {"required": False, "allow_null": True},
            "repair_space": {"required": False, "allow_null": True},
            "gas_station_count": {"required": False, "allow_null": True},
            "charging_pile_count": {"required": False, "allow_null": True},
            "car_wash_count": {"required": False, "allow_null": True},
            "office_flag": {"required": False, "allow_null": True},
            "canteen_flag": {"required": False, "allow_null": True},
            "dormitory_flag": {"required": False, "allow_null": True},
            "security_room_flag": {"required": False, "allow_null": True},
            "warehouse_flag": {"required": False, "allow_null": True},
            "training_room_flag": {"required": False, "allow_null": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
            # 小数字段类型配置
            "total_area": {"required": False, "allow_null": True, "max_digits": 10, "decimal_places": 2},
            "building_area": {"required": False, "allow_null": True, "max_digits": 10, "decimal_places": 2},
            # 坐标字段类型配置
            "lon02": {"required": False, "allow_null": True, "max_digits": 20, "decimal_places": 16},
            "lat02": {"required": False, "allow_null": True, "max_digits": 20, "decimal_places": 16},
            # 时间字段类型配置
            "oper_start_time": {"required": False, "allow_null": True, "format": "%H:%M:%S", "input_formats": ["%H:%M:%S", "%H:%M"]},
            "oper_end_time": {"required": False, "allow_null": True, "format": "%H:%M:%S", "input_formats": ["%H:%M:%S", "%H:%M"]},
        }

    def get_park_type_display(self, obj):
        """场地类型显示名称"""
        if obj.park_type == 0:
            return "场内"
        elif obj.park_type == 1:
            return "外停点"
        elif obj.park_type == 2:
            return "终点站"
        else:
            return "未知"

    def get_station_type_display(self, obj):
        """场站类型显示名称"""
        if obj.station_type == 0:
            return "总站"
        elif obj.station_type == 1:
            return "分站"
        elif obj.station_type == 2:
            return "停车场"
        elif obj.station_type == 3:
            return "维修中心"
        else:
            return "未知"

    def get_park_status_display(self, obj):
        """停车场状态显示名称"""
        if obj.park_status == 0:
            return "停用"
        elif obj.park_status == 1:
            return "建设中"
        elif obj.park_status == 2:
            return "运营中"
        else:
            return "未知"

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0

    def validate_park_name(self, value):
        """验证场站名称"""
        if not value or not value.strip():
            raise serializers.ValidationError("场站名称不能为空")
        return value.strip()

    def validate_total_area(self, value):
        """验证总面积"""
        if value is not None and value < 0:
            raise serializers.ValidationError("总面积不能为负数")
        return value

    def validate_building_area(self, value):
        """验证建筑面积"""
        if value is not None and value < 0:
            raise serializers.ValidationError("建筑面积不能为负数")
        return value

    def validate_park_type(self, value):
        """验证场地类型"""
        if value is not None and value not in [0, 1, 2]:
            raise serializers.ValidationError("场地类型只能是0(场内)、1(外停点)或2(终点站)")
        return value

    def validate_station_type(self, value):
        """验证场站类型"""
        if value is not None and value not in [0, 1, 2, 3]:
            raise serializers.ValidationError("场站类型只能是0(总站)、1(分站)、2(停车场)或3(维修中心)")
        return value

    def validate_park_status(self, value):
        """验证停车场状态"""
        if value is not None and value not in [0, 1, 2]:
            raise serializers.ValidationError("停车场状态只能是0(停用)、1(建设中)或2(运营中)")
        return value

    def validate_contact_phone(self, value):
        """验证联系电话"""
        if value:
            import re
            if not re.match(r'^[\d\-\+\(\)\s]+$', value):
                raise serializers.ValidationError("联系电话格式不正确")
        return value

    def validate_lon02(self, value):
        """验证经度"""
        if value is not None:
            if not (-180 <= value <= 180):
                raise serializers.ValidationError("经度必须在-180到180之间")
        return value

    def validate_lat02(self, value):
        """验证纬度"""
        if value is not None:
            if not (-90 <= value <= 90):
                raise serializers.ValidationError("纬度必须在-90到90之间")
        return value

    def validate(self, attrs):
        """整体验证"""
        # 验证运营开始时间和结束时间
        oper_start_time = attrs.get("oper_start_time")
        oper_end_time = attrs.get("oper_end_time")

        if oper_start_time and oper_end_time and oper_start_time >= oper_end_time:
            raise serializers.ValidationError("运营开始时间必须早于结束时间")

        # 验证建筑面积不能大于总面积
        total_area = attrs.get("total_area")
        building_area = attrs.get("building_area")

        if total_area and building_area and building_area > total_area:
            raise serializers.ValidationError("建筑面积不能大于总面积")

        return attrs


class ParkModelCreateSerializer(ParkModelSerializer):
    """
    停车场站创建序列化器

    功能说明:
    - 专门用于创建新场站时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(ParkModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            "park_name": {"required": True},
            "company_name": {"required": True},
        }

    def create(self, validated_data):
        """创建场站时自动生成GUID"""
        return super().create(validated_data)


class ParkModelUpdateSerializer(ParkModelSerializer):
    """
    停车场站更新序列化器

    功能说明:
    - 专门用于更新现有场站时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(ParkModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class ParkModelSimpleSerializer(CustomModelSerializer):
    """
    停车场站简单序列化器
    只返回核心字段：id、场站名称、场站编码
    """
    
    class Meta:
        model = ParkModel
        fields = ['id', 'park_code', 'park_name']
        read_only_fields = fields


class ParkModelListSerializer(ParkModelSerializer):
    """
    停车场站列表序列化器

    功能说明:
    - 专门用于场站列表显示,优化性能
    - 只包含列表展示需要的核心字段
    - 包含计算字段(状态、显示名称等)
    - 减少数据传输量,提高响应速度
    - 所有字段为只读,确保数据安全
    """

    class Meta:
        model = ParkModel
        fields = [
            # 基础信息字段
            "id",
            "park_name",
            "company_name",
            "park_code",
            "park_address",
            "lon02",
            "lat02",
            
            # 类型和状态字段
            "park_type",
            "station_type",
            "park_status",
            
            # 面积和容量字段
            "total_area",
            "building_area",
            "parking_space",
            "repair_space",
            
            # 设施数量字段
            "gas_station_count",
            "charging_pile_count",
            "car_wash_count",
            
            # 设施配置标记字段
            "repair_flag",
            "report_flag",
            "office_flag",
            "canteen_flag",
            "dormitory_flag",
            "security_room_flag",
            "warehouse_flag",
            "training_room_flag",
            
            # 运营信息字段
            "oper_start_time",
            "oper_end_time",
            "principal",
            "contact_phone",
            "contact_email",
            
            # 状态字段
            "enabled_mark",
            "delete_mark",
            
            # 计算显示字段
            "park_type_display",
            "station_type_display",
            "park_status_display",
            "is_enabled",
            
            # 审计字段
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
        ]
        read_only_fields = fields


class ParkModelMapSerializer(CustomModelSerializer):
    """
    停车场站地图序列化器（用于地图展示）
    
    功能说明：
    - 专门用于地图展示，包含WGS84坐标系坐标数据
    - 包含地图展示需要的核心字段
    - 优化数据传输，只包含地图展示必需的字段
    - 所有字段为只读，确保数据安全
    """
    
    class Meta:
        model = ParkModel
        fields = [
            # 基础信息字段
            "id",
            "park_code",
            "park_name",
            "company_name",
            "park_address",
            "station_type",
            "park_status",
            
            # WGS84坐标字段
            "lon84",
            "lat84",
        ]
        read_only_fields = fields

