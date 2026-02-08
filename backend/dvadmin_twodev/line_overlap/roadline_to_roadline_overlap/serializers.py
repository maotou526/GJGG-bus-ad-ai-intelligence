'''
Description: 公交线路复线情况序列化器
Version: 1.0
Author: 王晨
Date: 2025-01-XX
LastEditors: 
LastEditTime: 
'''
from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import RoadlineToRoadlineOverlapModel


class RoadlineToRoadlineOverlapSerializer(CustomModelSerializer):
    """
    公交线路复线情况序列化器
    用于数据的序列化和反序列化
    """
    
    # 计算字段 - 是否有效
    is_valid = serializers.ReadOnlyField(
        help_text="复线记录是否有效（在当前日期范围内）"
    )
    
    # 计算字段 - 段列表
    segment_list_02 = serializers.SerializerMethodField(
        help_text="02坐标系的段列表"
    )
    
    def get_segment_list_02(self, obj):
        """
        获取02坐标系的段列表
        """
        return obj.segment_list_02

    class Meta:
        model = RoadlineToRoadlineOverlapModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]
        extra_kwargs = {
            "main_roadline_detail": {
                "required": False,
                "allow_null": True,
                "help_text": "主线路的走向详情"
            },
            "main_roadline_code": {
                "required": False,
                "allow_null": True,
                "help_text": "主线路的行业线路编号"
            },
            "main_roadline_name": {
                "required": False,
                "allow_null": True,
                "help_text": "主线路名称"
            },
            "main_roadline_updown": {
                "required": False,
                "allow_null": True,
                "help_text": "主线路上下行：0上行，1下行"
            },
            "vice_roadline_detail": {
                "required": False,
                "allow_null": True,
                "help_text": "副线路的走向详情"
            },
            "vice_roadline_code": {
                "required": False,
                "allow_null": True,
                "help_text": "副线路的行业线路编号"
            },
            "vice_roadline_name": {
                "required": False,
                "allow_null": True,
                "help_text": "副线路名称"
            },
            "vice_roadline_updown": {
                "required": False,
                "allow_null": True,
                "help_text": "副线路上下行：0上行，1下行"
            },
            "repeat_line_length": {
                "required": False,
                "allow_null": True,
                "min_value": 0,
                "help_text": "复线长度（km）"
            },
            "main_repeat_rate": {
                "required": False,
                "allow_null": True,
                "help_text": "复线率（复线长度/主线路长度）"
            },
            "vice_repeat_rate": {
                "required": False,
                "allow_null": True,
                "help_text": "复线率（复线长度/副线路长度）"
            },
            "repeat_lon_lat02": {
                "required": False,
                "allow_null": True,
                "help_text": "GCJ02坐标系复线轨迹数据"
            },
            "exec_day": {
                "required": False,
                "allow_null": True,
                "help_text": "复线情况的启用日期"
            },
            "expiry_day": {
                "required": False,
                "allow_null": True,
                "help_text": "复线情况的截止日期"
            }
        }

    def validate_repeat_line_length(self, value):
        """
        验证复线长度
        """
        if value is not None and value < 0:
            raise serializers.ValidationError("复线长度不能为负数")
        
        return value

    def validate_main_repeat_rate(self, value):
        """
        验证主线路复线率
        """
        if value is not None and (value < 0 or value > 1):
            raise serializers.ValidationError("复线率必须在0到1之间")
        
        return value

    def validate_vice_repeat_rate(self, value):
        """
        验证副线路复线率
        """
        if value is not None and (value < 0 or value > 1):
            raise serializers.ValidationError("复线率必须在0到1之间")
        
        return value


class RoadlineToRoadlineOverlapCreateSerializer(RoadlineToRoadlineOverlapSerializer):
    """
    公交线路复线情况创建序列化器
    用于创建新记录时的数据验证
    """
    
    class Meta(RoadlineToRoadlineOverlapSerializer.Meta):
        """
        创建时不额外强制任何字段必填，完全复用基础序列化器的配置。
        由于模型上存在 unique_together 约束
        (main_roadline_detail, vice_roadline_detail, exec_day)，
        DRF 默认生成的 UniqueTogetherValidator 会把这些字段当作必填。
        这里通过 validators = [] 关闭该自动校验，避免出现“该字段是必填项”的错误。
        """
        extra_kwargs = RoadlineToRoadlineOverlapSerializer.Meta.extra_kwargs.copy()
        validators = []


class RoadlineToRoadlineOverlapUpdateSerializer(RoadlineToRoadlineOverlapSerializer):
    """
    公交线路复线情况更新序列化器
    用于更新记录时的数据验证
    """
    
    class Meta(RoadlineToRoadlineOverlapSerializer.Meta):
        extra_kwargs = RoadlineToRoadlineOverlapSerializer.Meta.extra_kwargs.copy()
        for field in extra_kwargs:
            extra_kwargs[field]["required"] = False


class RoadlineToRoadlineOverlapListSerializer(RoadlineToRoadlineOverlapSerializer):
    """
    公交线路复线情况列表序列化器
    用于列表显示
    """
    
    class Meta(RoadlineToRoadlineOverlapSerializer.Meta):
        fields = [
            "id",
            "main_roadline_code",
            "main_roadline_name",
            "main_roadline_updown",
            "vice_roadline_code",
            "vice_roadline_name",
            "vice_roadline_updown",
            "repeat_line_length",
            "main_repeat_rate",
            "vice_repeat_rate",
            "exec_day",
            "expiry_day",
            "is_valid",
            "create_datetime",
            "update_datetime",
            "creator_name",
            "modifier_name",
            "description"
        ]
        read_only_fields = fields

