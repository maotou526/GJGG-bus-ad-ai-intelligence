"""
Description: 车辆广告资源位序列化器
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import VehicleAdResourceModel


class VehicleAdResourceModelSerializer(CustomModelSerializer):
    """
    车辆广告资源位序列化器

    功能说明:
    - 提供车辆广告资源位数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer,获得审计字段自动填充功能
    """

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()

    # 计算字段 - 资源状态显示名称
    resource_status_display = serializers.SerializerMethodField()

    # 关联字段 - 车辆信息
    vehicle_plate = serializers.CharField(source='vehicle_id.vehicle_plate', read_only=True)
    vehicle_no = serializers.CharField(source='vehicle_id.vehicle_no', read_only=True)
    
    # 关联字段 - 线路信息
    roadline_id = serializers.CharField(source='vehicle_id.roadline_id', read_only=True, allow_null=True)
    roadline_name = serializers.CharField(source='vehicle_id.roadline_name', read_only=True, allow_null=True)

    # 关联字段 - 媒体类型信息
    media_type_name = serializers.CharField(source='base_media_type_id.media_name', read_only=True)
    # 列表展示用：若被折叠为组合媒体类型，则显示组合名称，否则显示基础媒体类型名称
    display_media_type_name = serializers.SerializerMethodField()

    class Meta:
        model = VehicleAdResourceModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            # 允许前端不传 resource_code：创建时会根据 vehicle_id + base_media_type_id 自动生成
            "resource_code": {"required": False, "allow_null": True, "allow_blank": True},
            "vehicle_id": {"required": True, "allow_null": False},
            "base_media_type_id": {"required": True, "allow_null": False},
            # 允许前端不传 resource_status：模型默认值为 1（空闲）
            "resource_status": {"required": False, "allow_null": True},
            "current_order_id": {"required": False, "allow_null": True},
            "scheduled_start_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "scheduled_end_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "on_air_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "off_air_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "remark": {"required": False, "allow_null": True, "allow_blank": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0

    def get_resource_status_display(self, obj):
        """资源状态显示名称"""
        # 自动判断：如果下刊日期超过投放结束日期，则为到期未下刊
        # 条件：off_air_date 和 scheduled_end_date 都存在，且 off_air_date > scheduled_end_date
        if (obj.off_air_date and obj.scheduled_end_date and 
            obj.off_air_date > obj.scheduled_end_date):
            return "到期未下刊"
        
        # 如果手动设置了状态 7，也显示为到期未下刊
        if obj.resource_status == 7:
            return "到期未下刊"
        
        status_map = {
            1: "空闲",
            2: "预订",
            3: "在刊",
            4: "下刊",
            5: "维修中",
            6: "不可用",
        }
        return status_map.get(obj.resource_status, "未知")

    def get_display_media_type_name(self, obj):
        """
        列表展示用媒体类型名称：
        - 默认：基础媒体类型名称
        - 若 viewset 在 context 中提供了 mapping（key 支持 vehicle_id|base_type_id），则显示组合名称
        """
        mapping = self.context.get("base_type_to_composite_name") or {}
        base_id = getattr(obj, "base_media_type_id_id", None) or getattr(obj.base_media_type_id, "id", None)
        base_id = str(base_id) if base_id is not None else None
        vehicle_id = getattr(obj, "vehicle_id_id", None) or getattr(obj.vehicle_id, "id", None)
        vehicle_id = str(vehicle_id) if vehicle_id is not None else None

        # 优先匹配 vehicle_id|base_id
        if vehicle_id and base_id:
            key = f"{vehicle_id}|{base_id}"
            if key in mapping:
                return mapping[key]
        # 兼容旧逻辑：仅 base_id
        if base_id and base_id in mapping:
            return mapping[base_id]
        return getattr(obj, "media_type_name", None) or (getattr(obj.base_media_type_id, "media_name", None) if obj.base_media_type_id else None)

    def validate_resource_code(self, value):
        """验证资源编码"""
        if not value or not value.strip():
            raise serializers.ValidationError("资源编码不能为空")
        return value.strip()

    def validate_resource_status(self, value):
        """验证资源状态"""
        if value not in [1, 2, 3, 4, 5, 6, 7]:
            raise serializers.ValidationError("资源状态只能是：1=空闲, 2=预订, 3=在刊, 4=下刊, 5=维修中, 6=不可用, 7=到期未下刊")
        return value

    def validate(self, attrs):
        """整体验证"""
        # 验证投放开始日期和结束日期
        scheduled_start_date = attrs.get("scheduled_start_date")
        scheduled_end_date = attrs.get("scheduled_end_date")

        if scheduled_start_date and scheduled_end_date and scheduled_start_date > scheduled_end_date:
            raise serializers.ValidationError("投放开始日期不能晚于结束日期")

        # 验证基础媒体类型必须是基础类型（非组合类型）
        base_media_type = attrs.get("base_media_type_id")
        if base_media_type:
            # 如果传入的是对象，直接检查
            if hasattr(base_media_type, 'is_composite') and base_media_type.is_composite:
                raise serializers.ValidationError("基础媒体类型必须是基础类型（is_composite=False），不能是组合类型")
            # 如果传入的是ID，需要查询数据库
            elif isinstance(base_media_type, int):
                from dvadmin_twodev.basedata.media_type.models import AdMediaTypeModel
                try:
                    media_type = AdMediaTypeModel.objects.get(id=base_media_type)
                    if media_type.is_composite:
                        raise serializers.ValidationError("基础媒体类型必须是基础类型（is_composite=False），不能是组合类型")
                except AdMediaTypeModel.DoesNotExist:
                    raise serializers.ValidationError("指定的媒体类型不存在")

        # 冲突检测：检查相同 vehicle_id 和 base_media_type_id 的日期范围是否重叠
        vehicle_id = attrs.get("vehicle_id")
        base_media_type_id = attrs.get("base_media_type_id")
        
        # 如果提供了日期信息，进行冲突检测
        if scheduled_start_date and scheduled_end_date and vehicle_id and base_media_type_id:
            # 创建临时对象用于冲突检测
            instance = self.instance if self.instance else VehicleAdResourceModel()
            instance.vehicle_id = vehicle_id
            instance.base_media_type_id = base_media_type_id
            instance.scheduled_start_date = scheduled_start_date
            instance.scheduled_end_date = scheduled_end_date
            
            # 获取要排除的ID（更新时排除自身）
            exclude_id = None
            if self.instance and hasattr(self.instance, 'pk') and self.instance.pk:
                exclude_id = self.instance.pk
            
            # 执行冲突检测
            has_conflict, conflicts = instance.check_schedule_conflict(exclude_id=exclude_id)
            
            if has_conflict:
                conflict_info = []
                for conflict in conflicts:
                    conflict_info.append(
                        f"资源编码: {conflict.resource_code}, "
                        f"日期范围: {conflict.scheduled_start_date} 至 {conflict.scheduled_end_date}"
                    )
                raise serializers.ValidationError(
                    f"排期冲突：相同车辆和媒体类型的日期范围不能重叠。冲突的资源位：{'; '.join(conflict_info)}"
                )

        return attrs


class VehicleAdResourceModelCreateSerializer(VehicleAdResourceModelSerializer):
    """
    车辆广告资源位创建序列化器

    功能说明:
    - 专门用于创建新资源位时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    # 显式声明：避免在部分场景下 DRF 根据模型推断为必填
    scheduled_start_date = serializers.DateField(
        required=False,
        allow_null=True,
        format="%Y-%m-%d",
        input_formats=["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"],
    )
    scheduled_end_date = serializers.DateField(
        required=False,
        allow_null=True,
        format="%Y-%m-%d",
        input_formats=["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"],
    )

    def __init__(self, *args, **kwargs):
        """
        兜底：在批量新增/简化新增场景下，明确取消投放开始/结束日期必填。
        有些场景下 DRF/父类字段推断可能导致 required 被覆盖，这里强制修正。
        """
        super().__init__(*args, **kwargs)
        for f in ("scheduled_start_date", "scheduled_end_date"):
            if f in self.fields:
                self.fields[f].required = False
                self.fields[f].allow_null = True

    class Meta(VehicleAdResourceModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            **VehicleAdResourceModelSerializer.Meta.extra_kwargs,
            "resource_code": {"required": False, "allow_null": True, "allow_blank": True},
            "vehicle_id": {"required": True, "allow_null": False},
            "base_media_type_id": {"required": True, "allow_null": False},
            "resource_status": {"required": False, "allow_null": True},
            # 批量新增/简化新增场景：投放开始/结束日期先不做必填
            "scheduled_start_date": {
                "required": False,
                "allow_null": True,
                "format": "%Y-%m-%d",
                "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"],
            },
            "scheduled_end_date": {
                "required": False,
                "allow_null": True,
                "format": "%Y-%m-%d",
                "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"],
            },
        }

    def create(self, validated_data):
        """创建资源位时自动生成资源编码（如果未提供）"""
        resource_code = validated_data.get('resource_code')
        if not resource_code:
            vehicle = validated_data.get('vehicle_id')
            media_type = validated_data.get('base_media_type_id')
            if vehicle and media_type:
                # 自动生成资源编码：车辆编号-媒体类型名称
                vehicle_no = getattr(vehicle, 'vehicle_no', '') or getattr(vehicle, 'vehicle_plate', '')
                media_name = getattr(media_type, 'media_name', '')
                validated_data['resource_code'] = f"{vehicle_no}-{media_name}"
        # 默认资源状态为空闲
        if validated_data.get("resource_status") in (None, ""):
            validated_data["resource_status"] = 1
        return super().create(validated_data)


class VehicleAdResourceModelUpdateSerializer(VehicleAdResourceModelSerializer):
    """
    车辆广告资源位更新序列化器

    功能说明:
    - 专门用于更新现有资源位时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(VehicleAdResourceModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime", "resource_code", "vehicle_id", "base_media_type_id"]


class VehicleAdResourceModelListSerializer(VehicleAdResourceModelSerializer):
    """
    车辆广告资源位列表序列化器

    功能说明:
    - 专门用于资源位列表显示,优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量,提高响应速度
    - 所有字段为只读,确保数据安全
    """

    class Meta:
        model = VehicleAdResourceModel
        fields = [
            # 基础信息字段
            "id",
            "resource_code",
            "vehicle_id",
            "vehicle_plate",
            "vehicle_no",
            "roadline_id",
            "roadline_name",
            "base_media_type_id",
            "media_type_name",
            "display_media_type_name",
            
            # 状态字段
            "resource_status",
            "resource_status_display",
            "current_order_id",
            
            # 日期信息
            "scheduled_start_date",
            "scheduled_end_date",
            
            # 备注
            "remark",
            
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

