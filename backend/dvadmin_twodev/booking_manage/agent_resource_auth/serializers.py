"""
Description: 代理商资源授权序列化器
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import AgentResourceAuthModel


class AgentResourceAuthModelSerializer(CustomModelSerializer):
    """
    代理商资源授权序列化器

    功能说明:
    - 提供代理商资源授权数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer,获得审计字段自动填充功能
    """

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()

    # 计算字段 - 资源类型显示名称
    resource_type_display = serializers.SerializerMethodField()

    # 计算字段 - 资源名称（根据类型动态获取）
    resource_name = serializers.SerializerMethodField()

    # 关联字段 - 代理商信息
    agent_code = serializers.CharField(source='agent_id.agent_code', read_only=True)
    company_name = serializers.CharField(source='agent_id.company_name', read_only=True)

    class Meta:
        model = AgentResourceAuthModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "agent_id": {"required": True, "allow_null": False},
            "resource_type": {"required": True, "allow_null": False},
            "resource_id": {"required": True, "allow_null": False},
            "auth_start_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "auth_end_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0

    def get_resource_type_display(self, obj):
        """资源类型显示名称"""
        type_map = {
            1: "线路",
            2: "车辆",
            3: "媒体类型",
        }
        return type_map.get(obj.resource_type, "未知")

    def get_resource_name(self, obj):
        """根据资源类型获取资源名称"""
        try:
            if obj.resource_type == 1:  # 线路
                from dvadmin_twodev.basedata.roadline.models import RoadlineModel
                resource = RoadlineModel.objects.filter(id=obj.resource_id, delete_mark=0).first()
                return resource.line_name if resource else f"线路ID:{obj.resource_id}"
            elif obj.resource_type == 2:  # 车辆
                from dvadmin_twodev.basedata.vehicle.models import VehicleModel
                resource = VehicleModel.objects.filter(id=obj.resource_id, delete_mark=0).first()
                if resource:
                    return f"{resource.vehicle_plate or ''} {resource.vehicle_no or ''}".strip() or f"车辆ID:{obj.resource_id}"
                return f"车辆ID:{obj.resource_id}"
            elif obj.resource_type == 3:  # 媒体类型
                from dvadmin_twodev.basedata.media_type.models import AdMediaTypeModel
                resource = AdMediaTypeModel.objects.filter(id=obj.resource_id, delete_mark=0).first()
                return resource.media_name if resource else f"媒体类型ID:{obj.resource_id}"
            else:
                return f"资源ID:{obj.resource_id}"
        except Exception:
            return f"资源ID:{obj.resource_id}"

    def validate_resource_type(self, value):
        """验证资源类型"""
        if value not in [1, 2, 3]:
            raise serializers.ValidationError("资源类型只能是：1=线路, 2=车辆, 3=媒体类型")
        return value

    def validate_resource_id(self, value):
        """验证资源ID"""
        if value is None:
            raise serializers.ValidationError("资源ID不能为空")
        # resource_id 支持 UUID 字符串（以及历史上可能存在的整型ID）
        if isinstance(value, (int, float)):
            if value <= 0:
                raise serializers.ValidationError("资源ID必须大于0")
            return value
        if isinstance(value, str):
            if not value.strip():
                raise serializers.ValidationError("资源ID不能为空")
            return value.strip()
        # 其他类型统一转字符串（尽量兼容）
        return str(value)

    def validate(self, attrs):
        """整体验证"""
        # 验证授权日期
        auth_start_date = attrs.get("auth_start_date")
        auth_end_date = attrs.get("auth_end_date")

        if auth_start_date and auth_end_date and auth_start_date > auth_end_date:
            raise serializers.ValidationError("授权开始日期不能晚于授权结束日期")

        # 验证资源是否存在
        resource_type = attrs.get("resource_type")
        resource_id = attrs.get("resource_id")
        
        if resource_type and resource_id:
            try:
                if resource_type == 1:  # 线路
                    from dvadmin_twodev.basedata.roadline.models import RoadlineModel
                    if not RoadlineModel.objects.filter(id=resource_id, delete_mark=0).exists():
                        raise serializers.ValidationError("指定的线路不存在或已删除")
                elif resource_type == 2:  # 车辆
                    from dvadmin_twodev.basedata.vehicle.models import VehicleModel
                    if not VehicleModel.objects.filter(id=resource_id, delete_mark=0).exists():
                        raise serializers.ValidationError("指定的车辆不存在或已删除")
                elif resource_type == 3:  # 媒体类型
                    from dvadmin_twodev.basedata.media_type.models import AdMediaTypeModel
                    if not AdMediaTypeModel.objects.filter(id=resource_id, delete_mark=0).exists():
                        raise serializers.ValidationError("指定的媒体类型不存在或已删除")
            except ImportError:
                # 如果模型导入失败，跳过验证
                pass

        return attrs


class AgentResourceAuthModelCreateSerializer(AgentResourceAuthModelSerializer):
    """
    代理商资源授权创建序列化器

    功能说明:
    - 专门用于创建新授权时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(AgentResourceAuthModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            **AgentResourceAuthModelSerializer.Meta.extra_kwargs,
            "agent_id": {"required": True, "allow_null": False},
            "resource_type": {"required": True, "allow_null": False},
            "resource_id": {"required": True, "allow_null": False},
        }


class AgentResourceAuthModelUpdateSerializer(AgentResourceAuthModelSerializer):
    """
    代理商资源授权更新序列化器

    功能说明:
    - 专门用于更新现有授权时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(AgentResourceAuthModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime", "agent_id", "resource_type", "resource_id"]


class AgentResourceAuthModelListSerializer(AgentResourceAuthModelSerializer):
    """
    代理商资源授权列表序列化器

    功能说明:
    - 专门用于授权列表显示,优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量,提高响应速度
    - 所有字段为只读,确保数据安全
    """

    class Meta:
        model = AgentResourceAuthModel
        fields = [
            # 基础信息字段
            "id",
            "agent_id",
            "agent_code",
            "company_name",
            "resource_type",
            "resource_type_display",
            "resource_id",
            "resource_name",
            
            # 授权日期
            "auth_start_date",
            "auth_end_date",
            
            # 计算显示字段
            "is_enabled",
            
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

