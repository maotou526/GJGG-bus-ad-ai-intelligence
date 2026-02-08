from .models import OsmNodeWayRelModel
from dvadmin.utils.viewset import CustomModelViewSet
from .serializers import (
    OsmNodeWayRelSerializer,
    OsmNodeWayRelCreateSerializer,
    OsmNodeWayRelUpdateSerializer,
    OsmNodeWayRelListSerializer,
    OsmNodeWayRelExportSerializer
)


class OsmNodeWayRelModelViewSet(CustomModelViewSet):
    """
    OSM道路节点关联数据管理
    提供标准的 CRUD 接口
    """
    
    queryset = OsmNodeWayRelModel.objects.all()
    serializer_class = OsmNodeWayRelSerializer
    create_serializer_class = OsmNodeWayRelCreateSerializer
    update_serializer_class = OsmNodeWayRelUpdateSerializer
    list_serializer_class = OsmNodeWayRelListSerializer
    export_serializer_class = OsmNodeWayRelExportSerializer
