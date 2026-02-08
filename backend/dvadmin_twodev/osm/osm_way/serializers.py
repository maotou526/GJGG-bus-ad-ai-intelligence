from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import OsmWayModel


class OsmWaySerializer(CustomModelSerializer):
    """
    OSM道路数据序列化器
    用于数据的序列化和反序列化
    """
    
    # 计算字段 - 道路名称显示
    name_display = serializers.ReadOnlyField(
        help_text="道路名称显示"
    )

    class Meta:
        model = OsmWayModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OsmWayCreateSerializer(CustomModelSerializer):
    """
    OSM道路创建序列化器
    """
    
    class Meta:
        model = OsmWayModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OsmWayUpdateSerializer(CustomModelSerializer):
    """
    OSM道路更新序列化器
    """
    
    class Meta:
        model = OsmWayModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OsmWayListSerializer(CustomModelSerializer):
    """
    OSM道路列表序列化器
    """
    
    name_display = serializers.ReadOnlyField()

    class Meta:
        model = OsmWayModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OsmWayExportSerializer(CustomModelSerializer):
    """
    OSM道路导出序列化器
    """
    
    class Meta:
        model = OsmWayModel
        fields = "__all__"

