from .models import OsmWayModel
from dvadmin.utils.viewset import CustomModelViewSet
from .serializers import (
    OsmWaySerializer,
    OsmWayCreateSerializer,
    OsmWayUpdateSerializer,
    OsmWayListSerializer,
    OsmWayExportSerializer
)


class OsmWayModelViewSet(CustomModelViewSet):
    """
    OSM道路数据管理
    提供标准的 CRUD 接口
    """
    
    queryset = OsmWayModel.objects.all()
    serializer_class = OsmWaySerializer
    create_serializer_class = OsmWayCreateSerializer
    update_serializer_class = OsmWayUpdateSerializer
    list_serializer_class = OsmWayListSerializer
    export_serializer_class = OsmWayExportSerializer
