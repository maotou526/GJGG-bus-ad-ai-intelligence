from .models import OsmNodeModel
from dvadmin.utils.viewset import CustomModelViewSet
from .serializers import (
    OsmNodeSerializer,
    OsmNodeCreateSerializer,
    OsmNodeUpdateSerializer,
    OsmNodeListSerializer,
    OsmNodeExportSerializer
)


class OsmNodeModelViewSet(CustomModelViewSet):
    """
    OSM节点数据管理
    提供标准的 CRUD 接口
    """
    
    queryset = OsmNodeModel.objects.all()
    serializer_class = OsmNodeSerializer
    create_serializer_class = OsmNodeCreateSerializer
    update_serializer_class = OsmNodeUpdateSerializer
    list_serializer_class = OsmNodeListSerializer
    export_serializer_class = OsmNodeExportSerializer
