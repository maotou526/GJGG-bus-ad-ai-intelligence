from rest_framework import serializers
from dvadmin.utils.serializers import CustomModelSerializer
from .models import OsmNodeModel


class OsmNodeSerializer(CustomModelSerializer):
    """
    OSM节点数据序列化器
    用于数据的序列化和反序列化
    """
    
    # 计算字段 - 格式化坐标显示
    coordinate_display = serializers.ReadOnlyField(
        help_text="格式化的坐标显示"
    )

    class Meta:
        model = OsmNodeModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OsmNodeCreateSerializer(CustomModelSerializer):
    """
    OSM节点创建序列化器
    """
    
    class Meta:
        model = OsmNodeModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OsmNodeUpdateSerializer(CustomModelSerializer):
    """
    OSM节点更新序列化器
    """
    
    class Meta:
        model = OsmNodeModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OsmNodeListSerializer(CustomModelSerializer):
    """
    OSM节点列表序列化器
    """
    
    coordinate_display = serializers.ReadOnlyField()

    class Meta:
        model = OsmNodeModel
        fields = "__all__"
        read_only_fields = ["id", "create_datetime", "update_datetime"]


class OsmNodeExportSerializer(CustomModelSerializer):
    """
    OSM节点导出序列化器
    """
    
    class Meta:
        model = OsmNodeModel
        fields = "__all__"

