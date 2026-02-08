"""
Description: 媒体类型组合关系模型序列化器
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
"""

from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import AdMediaTypeCompositionModel
from dvadmin_twodev.basedata.media_type.models import AdMediaTypeModel


class AdMediaTypeCompositionModelSerializer(CustomModelSerializer):
    """
    媒体类型组合关系模型序列化器

    功能说明：
    - 提供媒体类型组合关系数据的序列化和反序列化功能
    - 包含所有字段的完整序列化
    - 自动计算显示字段（如类型名称等）
    - 提供数据验证功能
    - 支持创建、更新、查询等操作

    继承自CustomModelSerializer，获得审计字段自动填充功能
    """

    # 计算字段 - 组合类型名称
    composite_type_name = serializers.SerializerMethodField()

    # 计算字段 - 基础类型名称
    component_type_name = serializers.SerializerMethodField()

    class Meta:
        model = AdMediaTypeCompositionModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "composite_type_id": {"required": True, "allow_null": False},
            "component_type_id": {"required": True, "allow_null": False},
            "sort_order": {"required": False, "allow_null": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def get_composite_type_name(self, obj):
        """获取组合类型名称"""
        if obj.composite_type_id:
            try:
                # 如果是 ForeignKey 对象，直接访问
                if hasattr(obj.composite_type_id, 'media_name'):
                    return obj.composite_type_id.media_name
                # 如果是 ID 字符串，查询对象
                media_type = AdMediaTypeModel.objects.filter(id=obj.composite_type_id).first()
                return media_type.media_name if media_type else "未找到"
            except Exception:
                return "未找到"
        return None

    def get_component_type_name(self, obj):
        """获取基础类型名称"""
        if obj.component_type_id:
            try:
                # 如果是 ForeignKey 对象，直接访问
                if hasattr(obj.component_type_id, 'media_name'):
                    return obj.component_type_id.media_name
                # 如果是 ID 字符串，查询对象
                media_type = AdMediaTypeModel.objects.filter(id=obj.component_type_id).first()
                return media_type.media_name if media_type else "未找到"
            except Exception:
                return "未找到"
        return None

    def validate_composite_type_id(self, value):
        """验证组合类型ID"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"=== 验证组合类型ID ===")
        logger.info(f"接收到的组合类型ID: {value}, 类型: {type(value)}")
        
        if not value:
            logger.warning("组合类型ID为空")
            raise serializers.ValidationError("组合类型ID不能为空")
        
        # 确保是字符串类型
        if not isinstance(value, str):
            value = str(value)
        
        # 检查是否存在且为组合类型
        try:
            # 使用 get 方法，如果不存在会抛出异常
            media_type = AdMediaTypeModel.objects.get(id=value, delete_mark=0)
            logger.info(f"成功获取组合类型: id={media_type.id}, media_name={media_type.media_name}, is_composite={media_type.is_composite}")
            
            if not media_type.is_composite:
                logger.warning(f"类型不是组合类型: is_composite={media_type.is_composite}")
                raise serializers.ValidationError("指定的类型不是组合类型")
            
            logger.info(f"组合类型验证通过")
        except AdMediaTypeModel.DoesNotExist:
            logger.error(f"组合类型不存在或已删除: id={value}")
            raise serializers.ValidationError("组合类型不存在或已删除")
        except Exception as e:
            # 记录其他异常，便于调试
            logger.error(f"验证组合类型ID时出错: {value}, 错误类型: {type(e)}, 错误信息: {str(e)}")
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            raise serializers.ValidationError(f"组合类型验证失败: {str(e)}")
        
        # 返回ID字符串
        return value

    def validate_component_type_id(self, value):
        """验证基础类型ID"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info(f"=== 验证基础类型ID ===")
        logger.info(f"接收到的基础类型ID: {value}, 类型: {type(value)}")
        
        if not value:
            logger.warning("基础类型ID为空")
            raise serializers.ValidationError("基础类型ID不能为空")
        
        # 确保是字符串类型
        if not isinstance(value, str):
            value = str(value)
        
        # 检查是否存在且为基础类型
        try:
            # 使用 get 方法，如果不存在会抛出异常
            media_type = AdMediaTypeModel.objects.get(id=value, delete_mark=0)
            logger.info(f"成功获取基础类型: id={media_type.id}, media_name={media_type.media_name}, is_composite={media_type.is_composite}")
            
            if media_type.is_composite:
                logger.warning(f"类型不是基础类型: is_composite={media_type.is_composite}")
                raise serializers.ValidationError("指定的类型不是基础类型")
            
            logger.info(f"基础类型验证通过")
        except AdMediaTypeModel.DoesNotExist:
            logger.error(f"基础类型不存在或已删除: id={value}")
            raise serializers.ValidationError("基础类型不存在或已删除")
        except Exception as e:
            # 记录其他异常，便于调试
            logger.error(f"验证基础类型ID时出错: {value}, 错误类型: {type(e)}, 错误信息: {str(e)}")
            import traceback
            logger.error(f"错误堆栈: {traceback.format_exc()}")
            raise serializers.ValidationError(f"基础类型验证失败: {str(e)}")
        
        # 返回ID字符串
        return value

    def validate_sort_order(self, value):
        """验证显示顺序"""
        if value is not None and value < 0:
            raise serializers.ValidationError("显示顺序不能为负数")
        return value

    def validate(self, attrs):
        """整体验证"""
        composite_type_id = attrs.get("composite_type_id")
        component_type_id = attrs.get("component_type_id")
        
        # 防止组合类型和基础类型相同
        if composite_type_id and component_type_id and composite_type_id == component_type_id:
            raise serializers.ValidationError({
                "component_type_id": "组合类型和基础类型不能相同"
            })
        
        return attrs


class AdMediaTypeCompositionModelCreateSerializer(AdMediaTypeCompositionModelSerializer):
    """
    媒体类型组合关系创建序列化器

    功能说明：
    - 专门用于创建新组合关系时的数据验证
    - 继承基础序列化器的所有功能
    - 设置创建时的必填字段
    - 确保数据完整性
    """

    class Meta(AdMediaTypeCompositionModelSerializer.Meta):
        # 创建时必填字段
        extra_kwargs = {
            "composite_type_id": {"required": True},
            "component_type_id": {"required": True},
            "sort_order": {"required": False, "allow_null": True},
            "enabled_mark": {"required": False, "allow_null": True},
            "delete_mark": {"required": False, "allow_null": True},
        }

    def create(self, validated_data):
        """创建组合关系"""
        # 调用父类的create方法
        return super().create(validated_data)


class AdMediaTypeCompositionModelUpdateSerializer(AdMediaTypeCompositionModelSerializer):
    """
    媒体类型组合关系更新序列化器

    功能说明：
    - 专门用于更新现有组合关系时的数据验证
    - 继承基础序列化器的所有功能
    - 防止修改主键ID和创建时间
    - 允许部分字段更新
    - 保持数据一致性
    """

    class Meta(AdMediaTypeCompositionModelSerializer.Meta):
        # 更新时主键不可修改
        read_only_fields = ["id", "create_datetime", "update_datetime"]

    def validate(self, attrs):
        """更新时的验证"""
        # 调用父类验证
        attrs = super().validate(attrs)
        
        # 更新时检查唯一约束
        composite_type_id = attrs.get("composite_type_id", self.instance.composite_type_id)
        component_type_id = attrs.get("component_type_id", self.instance.component_type_id)
        
        # 检查是否存在重复的组合关系（排除当前记录）
        if composite_type_id and component_type_id:
            existing = AdMediaTypeCompositionModel.objects.filter(
                composite_type_id=composite_type_id,
                component_type_id=component_type_id,
                delete_mark=0
            ).exclude(id=self.instance.id).first()
            
            if existing:
                raise serializers.ValidationError({
                    "component_type_id": "该组合关系已存在"
                })
        
        return attrs


class AdMediaTypeCompositionModelListSerializer(AdMediaTypeCompositionModelSerializer):
    """
    媒体类型组合关系列表序列化器

    功能说明：
    - 专门用于组合关系列表显示，优化性能
    - 只包含列表展示需要的核心字段
    - 包含计算字段（类型名称等）
    - 减少数据传输量，提高响应速度
    - 所有字段为只读，确保数据安全
    """

    class Meta:
        model = AdMediaTypeCompositionModel
        fields = [
            # 基础信息字段
            "id",
            "composite_type_id",
            "component_type_id",
            "sort_order",
            
            # 计算显示字段
            "composite_type_name",
            "component_type_name",
            
            # 状态字段
            "enabled_mark",
            "delete_mark",
            
            # 审计字段
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description",
        ]
        read_only_fields = fields

