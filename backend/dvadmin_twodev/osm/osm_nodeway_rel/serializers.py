from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import OsmNodeWayRelModel


class OsmNodeWayRelSerializer(CustomModelSerializer):
    """
    OSM道路节点关联数据序列化器
    用于数据的序列化和反序列化
    """
    
    # 计算字段 - 关联关系显示
    relation_display = serializers.ReadOnlyField(
        help_text="关联关系显示"
    )

    class Meta:
        model = OsmNodeWayRelModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OsmNodeWayRelCreateSerializer(CustomModelSerializer):
    """
    OSM道路节点关联创建序列化器
    """
    
    class Meta:
        model = OsmNodeWayRelModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OsmNodeWayRelUpdateSerializer(CustomModelSerializer):
    """
    OSM道路节点关联更新序列化器
    """
    
    class Meta:
        model = OsmNodeWayRelModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OsmNodeWayRelListSerializer(CustomModelSerializer):
    """
    OSM道路节点关联列表序列化器
    """
    
    relation_display = serializers.ReadOnlyField()

    class Meta:
        model = OsmNodeWayRelModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OsmNodeWayRelExportSerializer(CustomModelSerializer):
    """
    OSM道路节点关联导出序列化器
    """
    
    class Meta:
        model = OsmNodeWayRelModel
        fields = "__all__"

