"""
Description: 车位广告序列化器
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer

from .models import VehicleAdPositionModel


class VehicleAdPositionModelSerializer(CustomModelSerializer):
    """
    车位广告序列化器

    功能说明:
    - 提供车位广告数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer, 获得审计字段自动填充功能
    """

    # 计算字段 - 是否启用
    is_enabled = serializers.SerializerMethodField()

    # 分配状态显示名称
    allocation_status_display = serializers.SerializerMethodField()

    # 确认状态显示名称
    confirm_status_display = serializers.SerializerMethodField()

    # 基础媒体类型名称（从resource_id关联获取）
    base_media_type_name = serializers.SerializerMethodField()

    # 车牌号（从vehicle_id关联获取）
    vehicle_plate = serializers.SerializerMethodField()

    # 资源状态（从 dwd_vehicle_ad_resource 关联表获取）
    resource_status = serializers.SerializerMethodField()
    resource_status_display = serializers.SerializerMethodField()

    class Meta:
        model = VehicleAdPositionModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "booking_detail_id": {"required": True, "allow_null": False},
            "roadline_id": {"required": True, "allow_null": False},
            "roadline_name": {"required": False, "allow_null": True, "allow_blank": True},
            "roadline_company_id": {"required": True, "allow_null": False},
            "roadline_company_name": {"required": False, "allow_null": True, "allow_blank": True},
            "resource_id": {"required": True, "allow_null": False},
            "vehicle_id": {"required": True, "allow_null": False},
            "vehicle_no": {"required": False, "allow_null": True, "allow_blank": True},
            "reserved_start_date": {"required": True, "allow_null": False, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "reserved_end_date": {"required": True, "allow_null": False, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "actual_on_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "actual_off_date": {"required": False, "allow_null": True, "format": "%Y-%m-%d", "input_formats": ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]},
            "allocation_status": {"required": True, "allow_null": False},
            "media_type_id": {"required": False, "allow_null": True},
            "media_type_name": {"required": False, "allow_null": True, "allow_blank": True},
            "media_json": {"required": False, "allow_null": True},
            "confirm_status": {"required": False, "allow_null": False},
            "exclude_reason": {"required": False, "allow_null": True, "allow_blank": True},
            "confirm_user_id": {"required": False, "allow_null": True},
            "confirm_time": {"required": False, "allow_null": True, "format": "%Y-%m-%d %H:%M:%S", "input_formats": ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d"]},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_is_enabled(self, obj):
        """是否启用"""
        return obj.enabled_mark == 1 and obj.delete_mark == 0

    def get_allocation_status_display(self, obj):
        """分配状态显示名称"""
        status_map = {
            1: "已分配",
            2: "已上刊",
            3: "已下刊",
            4: "已取消",
        }
        return status_map.get(obj.allocation_status, "未知")

    def get_confirm_status_display(self, obj):
        """营运公司确认状态显示名称"""
        status_map = {
            1: "待确认",
            2: "已确认",
            3: "已剔除",
        }
        return status_map.get(obj.confirm_status, "未知")
    
    def get_base_media_type_name(self, obj):
        """获取基础媒体类型名称"""
        try:
            if obj.resource_id and hasattr(obj.resource_id, 'base_media_type_id'):
                base_media_type = obj.resource_id.base_media_type_id
                if base_media_type and hasattr(base_media_type, 'media_name'):
                    return base_media_type.media_name
        except Exception:
            pass
        return None
    
    def get_vehicle_plate(self, obj):
        """获取车牌号（从关联的车辆表获取）"""
        try:
            if obj.vehicle_id and hasattr(obj.vehicle_id, 'vehicle_plate'):
                return obj.vehicle_id.vehicle_plate
        except Exception:
            pass
        return None

    def get_resource_status(self, obj):
        """获取资源状态（从关联的资源位表获取）"""
        try:
            resource = getattr(obj, "resource_id", None)
            if resource and hasattr(resource, "resource_status"):
                return resource.resource_status
        except Exception:
            pass
        return None

    def get_resource_status_display(self, obj):
        """
        获取资源状态显示名称
        优先复用资源位上的日期逻辑：
        - 如果 off_air_date 和 scheduled_end_date 都存在且 off_air_date > scheduled_end_date，则判定为“到期未下刊”
        - 否则根据 resource_status 数值映射到中文名称
        """
        try:
            resource = getattr(obj, "resource_id", None)
        except Exception:
            resource = None

        if not resource:
            return None

        # 处理到期未下刊的特殊逻辑
        try:
            off_air_date = getattr(resource, "off_air_date", None)
            scheduled_end_date = getattr(resource, "scheduled_end_date", None)
            if off_air_date and scheduled_end_date and off_air_date > scheduled_end_date:
                return "到期未下刊"
        except Exception:
            # 日期比较异常时忽略，走下面的状态映射
            pass

        status = getattr(resource, "resource_status", None)
        if status == 7:
            return "到期未下刊"

        status_map = {
            1: "空闲",
            2: "预订",
            3: "在刊",
            4: "下刊",
            5: "维修中",
            6: "不可用",
        }
        return status_map.get(status, "未知") if status is not None else None

    def validate_allocation_status(self, value):
        """验证分配状态"""
        if value not in [1, 2, 3, 4]:
            raise serializers.ValidationError("分配状态只能是：1=已分配, 2=已上刊, 3=已下刊, 4=已取消")
        return value

    def validate(self, attrs):
        """整体验证"""
        reserved_start_date = attrs.get("reserved_start_date")
        reserved_end_date = attrs.get("reserved_end_date")
        if reserved_start_date and reserved_end_date and reserved_start_date > reserved_end_date:
            raise serializers.ValidationError("预订开始日期不能晚于预订结束日期")
        return attrs


class VehicleAdPositionModelCreateSerializer(VehicleAdPositionModelSerializer):
    """
    车位广告创建序列化器

    功能说明:
    - 专门用于创建新车位广告时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(VehicleAdPositionModelSerializer.Meta):
        extra_kwargs = {
            **VehicleAdPositionModelSerializer.Meta.extra_kwargs,
            "booking_detail_id": {"required": True, "allow_null": False},
            "roadline_id": {"required": True, "allow_null": False},
            "roadline_company_id": {"required": True, "allow_null": False},
            "resource_id": {"required": True, "allow_null": False},
            "vehicle_id": {"required": True, "allow_null": False},
            "reserved_start_date": {"required": True, "allow_null": False},
            "reserved_end_date": {"required": True, "allow_null": False},
            "allocation_status": {"required": True, "allow_null": False},
        }

    def create(self, validated_data):
        """创建车位广告时自动填充部分冗余字段"""
        roadline_id = validated_data.get("roadline_id")
        if roadline_id and not validated_data.get("roadline_name"):
            try:
                if hasattr(roadline_id, "line_name"):
                    validated_data["roadline_name"] = roadline_id.line_name
            except Exception:
                pass

        roadline_company_id = validated_data.get("roadline_company_id")
        if roadline_company_id and not validated_data.get("roadline_company_name"):
            try:
                if hasattr(roadline_company_id, "company_name"):
                    validated_data["roadline_company_name"] = roadline_company_id.company_name
            except Exception:
                pass

        vehicle_id = validated_data.get("vehicle_id")
        if vehicle_id and not validated_data.get("vehicle_no"):
            try:
                if hasattr(vehicle_id, "vehicle_no"):
                    validated_data["vehicle_no"] = vehicle_id.vehicle_no
            except Exception:
                pass

        return super().create(validated_data)


class VehicleAdPositionModelUpdateSerializer(VehicleAdPositionModelSerializer):
    """
    车位广告更新序列化器

    功能说明:
    - 专门用于更新现有车位广告时的数据验证
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(VehicleAdPositionModelSerializer.Meta):
        read_only_fields = ["id", "create_datetime", "update_datetime"]

    def update(self, instance, validated_data):
        """更新时自动填充部分冗余字段，并处理车辆变更时的资源位同步"""
        from dvadmin_twodev.basedata.vehicle_ad_resource.models import VehicleAdResourceModel
        from django.db import transaction
        
        roadline_id = validated_data.get("roadline_id")
        if roadline_id and roadline_id != instance.roadline_id:
            try:
                if hasattr(roadline_id, "line_name"):
                    validated_data["roadline_name"] = roadline_id.line_name
            except Exception:
                pass

        roadline_company_id = validated_data.get("roadline_company_id")
        if roadline_company_id and roadline_company_id != instance.roadline_company_id:
            try:
                if hasattr(roadline_company_id, "company_name"):
                    validated_data["roadline_company_name"] = roadline_company_id.company_name
            except Exception:
                pass

        vehicle_id = validated_data.get("vehicle_id")
        new_vehicle_id = vehicle_id
        
        # 处理 vehicle_id 可能是字符串或对象的情况
        if vehicle_id:
            if isinstance(vehicle_id, str):
                # 如果是字符串ID，需要转换为对象
                from dvadmin_twodev.basedata.vehicle.models import VehicleModel
                try:
                    new_vehicle_id = VehicleModel.objects.get(id=vehicle_id)
                except VehicleModel.DoesNotExist:
                    raise serializers.ValidationError(f"车辆ID {vehicle_id} 不存在")
            elif hasattr(vehicle_id, 'id'):
                # 如果已经是对象，获取其ID用于比较
                pass
        
        # 如果车辆ID改变了，需要同步更新 resource_id
        old_vehicle_id = instance.vehicle_id.id if hasattr(instance.vehicle_id, 'id') else instance.vehicle_id
        new_vehicle_id_for_compare = new_vehicle_id.id if hasattr(new_vehicle_id, 'id') else new_vehicle_id if new_vehicle_id else None
        
        # 保存变更前的数据（用于记录变更历史）
        before_data = None
        vehicle_changed = new_vehicle_id and new_vehicle_id_for_compare != old_vehicle_id
        if vehicle_changed:
            import json
            before_data = {
                "vehicle_id": str(instance.vehicle_id.id) if hasattr(instance.vehicle_id, 'id') else str(instance.vehicle_id),
                "vehicle_no": instance.vehicle_no,
                "resource_id": str(instance.resource_id.id) if instance.resource_id else None,
                "roadline_id": str(instance.roadline_id.id) if hasattr(instance.roadline_id, 'id') else str(instance.roadline_id),
                "roadline_name": instance.roadline_name,
                "roadline_company_id": str(instance.roadline_company_id.id) if hasattr(instance.roadline_company_id, 'id') else str(instance.roadline_company_id),
                "roadline_company_name": instance.roadline_company_name,
                "reserved_start_date": str(instance.reserved_start_date) if instance.reserved_start_date else None,
                "reserved_end_date": str(instance.reserved_end_date) if instance.reserved_end_date else None,
                "allocation_status": instance.allocation_status,
            }
        
        if vehicle_changed:
            try:
                if hasattr(new_vehicle_id, "vehicle_no"):
                    validated_data["vehicle_no"] = new_vehicle_id.vehicle_no
            except Exception:
                pass
            
            # 获取原有的 resource_id 的 base_media_type_id
            old_resource = instance.resource_id
            if not old_resource:
                raise serializers.ValidationError("原资源位不存在")
            
            base_media_type_id = old_resource.base_media_type_id
            if not base_media_type_id:
                raise serializers.ValidationError("原资源位的媒体类型不存在")
            
            # 获取预订日期（用于冲突检测）
            from datetime import datetime
            
            reserved_start_date = validated_data.get("reserved_start_date") or instance.reserved_start_date
            reserved_end_date = validated_data.get("reserved_end_date") or instance.reserved_end_date
            
            if not reserved_start_date or not reserved_end_date:
                raise serializers.ValidationError("预订开始日期和结束日期不能为空")
            
            # 确保日期是 date 对象而不是字符串
            if isinstance(reserved_start_date, str):
                try:
                    reserved_start_date = datetime.strptime(reserved_start_date, "%Y-%m-%d").date()
                except ValueError:
                    raise serializers.ValidationError(f"无效的开始日期格式: {reserved_start_date}")
            
            if isinstance(reserved_end_date, str):
                try:
                    reserved_end_date = datetime.strptime(reserved_end_date, "%Y-%m-%d").date()
                except ValueError:
                    raise serializers.ValidationError(f"无效的结束日期格式: {reserved_end_date}")
            
            # 确保 vehicle_id 是对象
            vehicle_id_obj = new_vehicle_id
            if not hasattr(new_vehicle_id, 'id'):
                from dvadmin_twodev.basedata.vehicle.models import VehicleModel
                vehicle_id_obj = VehicleModel.objects.get(id=new_vehicle_id)
            
            # ========== 冲突检测 1：检查车位分配（VehicleAdPositionModel）的冲突 ==========
            from django.db.models import Q
            position_conflicts = VehicleAdPositionModel.objects.filter(
                vehicle_id=vehicle_id_obj,
                resource_id__base_media_type_id=base_media_type_id,
                delete_mark=0,
                enabled_mark=1,
                allocation_status__in=[1, 2],  # 已分配或已上刊
            ).filter(
                # 时间段重叠检测：reserved_start_date <= end_date AND reserved_end_date >= start_date
                Q(reserved_start_date__lte=reserved_end_date) &
                Q(reserved_end_date__gte=reserved_start_date)
            ).exclude(
                id=instance.id  # 排除当前正在编辑的车位
            )
            
            if position_conflicts.exists():
                conflict_info = []
                for conflict in position_conflicts:
                    conflict_info.append(
                        f"车位ID: {conflict.id}, "
                        f"日期范围: {conflict.reserved_start_date} 至 {conflict.reserved_end_date}"
                    )
                raise serializers.ValidationError(
                    f"车位分配冲突：新车辆在该媒体类型和日期范围内已有其他车位分配。冲突的车位：{'; '.join(conflict_info)}"
                )
            
            # ========== 冲突检测 2：检查资源位（VehicleAdResourceModel）的冲突 ==========
            # 创建临时对象用于冲突检测
            temp_resource = VehicleAdResourceModel()
            temp_resource.vehicle_id = vehicle_id_obj
            temp_resource.base_media_type_id = base_media_type_id
            temp_resource.scheduled_start_date = reserved_start_date
            temp_resource.scheduled_end_date = reserved_end_date
            
            # 执行资源位冲突检测
            has_resource_conflict, resource_conflicts = temp_resource.check_schedule_conflict(exclude_id=None)
            
            if has_resource_conflict:
                conflict_info = []
                for conflict in resource_conflicts:
                    conflict_info.append(
                        f"资源编码: {conflict.resource_code}, "
                        f"日期范围: {conflict.scheduled_start_date} 至 {conflict.scheduled_end_date}"
                    )
                raise serializers.ValidationError(
                    f"资源位冲突：新车辆在该媒体类型和日期范围内已有资源位排期。冲突的资源位：{'; '.join(conflict_info)}"
                )
            
            # ========== 冲突检测通过后，查找或更新资源位 ==========
            # 获取原资源位
            old_resource = instance.resource_id
            
            # 查找是否已有完全匹配的资源位（排除原资源位，因为我们要检查是否需要更新）
            existing_resource = VehicleAdResourceModel.objects.filter(
                vehicle_id=vehicle_id_obj,
                base_media_type_id=base_media_type_id,
                scheduled_start_date=reserved_start_date,
                scheduled_end_date=reserved_end_date,
                delete_mark=0,
                enabled_mark=1
            ).exclude(id=old_resource.id).first()
            
            if existing_resource:
                # 如果找到了完全匹配的资源位（且不是原资源位），使用它
                # 检查原资源位是否还被其他车位使用
                other_positions_using_old_resource = VehicleAdPositionModel.objects.filter(
                    resource_id=old_resource,
                    delete_mark=0,
                    enabled_mark=1
                ).exclude(id=instance.id)
                
                # 如果原资源位没有被其他车位使用，删除它
                if not other_positions_using_old_resource.exists():
                    old_resource.delete()
                
                new_resource = existing_resource
            else:
                # 如果找不到完全匹配的资源位，更新原资源位
                # 生成新的资源编码
                vehicle_id_str = str(vehicle_id_obj.id if hasattr(vehicle_id_obj, 'id') else vehicle_id_obj)
                media_type_id_str = str(base_media_type_id.id if hasattr(base_media_type_id, 'id') else base_media_type_id)
                # 使用 UUID 的前 8 个字符（去掉连字符）
                vehicle_short = vehicle_id_str.replace('-', '')[:8] if len(vehicle_id_str) > 8 else vehicle_id_str
                media_type_short = media_type_id_str.replace('-', '')[:8] if len(media_type_id_str) > 8 else media_type_id_str
                # 使用日期格式 YYYYMMDD 而不是 YYYY-MM-DD 以缩短长度
                # 日期现在是 date 对象，需要格式化为字符串
                start_date_short = reserved_start_date.strftime("%Y%m%d") if reserved_start_date else ''
                end_date_short = reserved_end_date.strftime("%Y%m%d") if reserved_end_date else ''
                resource_code = f"V{vehicle_short}M{media_type_short}{start_date_short}{end_date_short}"
                
                # 如果仍然超过 64 个字符，截断
                if len(resource_code) > 64:
                    resource_code = resource_code[:64]
                
                # 更新原资源位
                old_resource.vehicle_id = vehicle_id_obj
                old_resource.base_media_type_id = base_media_type_id
                old_resource.resource_code = resource_code
                old_resource.scheduled_start_date = reserved_start_date
                old_resource.scheduled_end_date = reserved_end_date
                old_resource.resource_status = 2  # 预订状态
                old_resource.current_order_id = None  # 订单 ID 是 UUID，无法存储在 IntegerField 中
                old_resource.save()
                
                # 使用更新后的原资源位
                new_resource = old_resource
            
            # 更新 resource_id 和 vehicle_id（确保是对象形式）
            validated_data["resource_id"] = new_resource
            validated_data["vehicle_id"] = vehicle_id_obj

        # 执行更新
        updated_instance = super().update(instance, validated_data)
        
        # 如果车辆改变了，插入变更记录
        if vehicle_changed:
            from dvadmin_twodev.booking_manage.vehicle_ad_position_change.models import VehicleAdPositionChangeModel
            from django.utils import timezone
            import json
            
            # 获取变更后的数据
            after_data = {
                "vehicle_id": str(updated_instance.vehicle_id.id) if hasattr(updated_instance.vehicle_id, 'id') else str(updated_instance.vehicle_id),
                "vehicle_no": updated_instance.vehicle_no,
                "resource_id": str(updated_instance.resource_id.id) if updated_instance.resource_id else None,
                "roadline_id": str(updated_instance.roadline_id.id) if hasattr(updated_instance.roadline_id, 'id') else str(updated_instance.roadline_id),
                "roadline_name": updated_instance.roadline_name,
                "roadline_company_id": str(updated_instance.roadline_company_id.id) if hasattr(updated_instance.roadline_company_id, 'id') else str(updated_instance.roadline_company_id),
                "roadline_company_name": updated_instance.roadline_company_name,
                "reserved_start_date": str(updated_instance.reserved_start_date) if updated_instance.reserved_start_date else None,
                "reserved_end_date": str(updated_instance.reserved_end_date) if updated_instance.reserved_end_date else None,
                "allocation_status": updated_instance.allocation_status,
            }
            
            # 获取订单ID和明细ID
            booking_order_id = None
            booking_detail_id = updated_instance.booking_detail_id
            if booking_detail_id:
                # booking_detail_id 是 ForeignKey，直接访问 booking_order_id
                try:
                    booking_order_id = booking_detail_id.booking_order_id
                except AttributeError:
                    # 如果 booking_detail_id 是对象但没有 booking_order_id 属性，尝试从数据库重新加载
                    from dvadmin_twodev.booking_manage.booking_order_detail.models import BookingOrderDetailModel
                    try:
                        detail = BookingOrderDetailModel.objects.get(id=booking_detail_id.id if hasattr(booking_detail_id, 'id') else booking_detail_id)
                        booking_order_id = detail.booking_order_id
                    except:
                        pass
            
            # 获取当前用户（从 request 中获取）
            operator_id = None
            request = self.context.get('request', None)
            if request and hasattr(request, 'user') and request.user.is_authenticated:
                operator_id = request.user
            
            # 创建变更记录
            VehicleAdPositionChangeModel.objects.create(
                booking_order_id=booking_order_id,
                booking_detail_id=booking_detail_id,
                action_type=3,  # 3=修改车位
                position_id=updated_instance,
                roadline_id=updated_instance.roadline_id,
                roadline_name=updated_instance.roadline_name,
                roadline_company_id=updated_instance.roadline_company_id,
                roadline_company_name=updated_instance.roadline_company_name,
                vehicle_id=updated_instance.vehicle_id,
                vehicle_no=updated_instance.vehicle_no,
                resource_id=updated_instance.resource_id,
                before_data=json.dumps(before_data, ensure_ascii=False) if before_data else None,
                after_data=json.dumps(after_data, ensure_ascii=False),
                change_reason="编辑车位：修改车辆",
                change_node="编辑",  # 变更节点，可以根据实际情况设置
                operator_id=operator_id,
                operation_time=timezone.now(),
            )
        
        return updated_instance


class VehicleAdPositionModelListSerializer(VehicleAdPositionModelSerializer):
    """
    车位广告列表序列化器

    功能说明:
    - 专门用于车位广告列表显示, 优化性能
    - 只包含列表展示需要的核心字段
    - 减少数据传输量, 提高响应速度
    - 所有字段为只读, 确保数据安全
    """

    class Meta:
        model = VehicleAdPositionModel
        fields = [
            # 基础信息
            "id",
            "booking_detail_id",
            # 线路与公司
            "roadline_id",
            "roadline_name",
            "roadline_company_id",
            "roadline_company_name",
            # 资源与车辆
            "resource_id",
            "resource_status",
            "resource_status_display",
            "vehicle_id",
            "vehicle_no",
            "vehicle_plate",
            # 媒体类型
            "media_type_id",
            "media_type_name",
            "media_json",
            "base_media_type_name",
            # 时间信息
            "reserved_start_date",
            "reserved_end_date",
            "actual_on_date",
            "actual_off_date",
            # 状态信息
            "allocation_status",
            "allocation_status_display",
            # 营运公司确认
            "confirm_status",
            "confirm_status_display",
            "exclude_reason",
            "confirm_user_id",
            "confirm_time",
            # 计算字段
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


