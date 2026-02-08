'''
Description: 公交线路复线情况视图集
Version: 1.0
Author: 王晨
Date: 2025-01-XX
LastEditors: 
LastEditTime: 
'''
from .models import RoadlineToRoadlineOverlapModel
from dvadmin.utils.viewset import CustomModelViewSet
from .serializers import (
    RoadlineToRoadlineOverlapSerializer,
    RoadlineToRoadlineOverlapCreateSerializer,
    RoadlineToRoadlineOverlapUpdateSerializer,
    RoadlineToRoadlineOverlapListSerializer,
)


class RoadlineToRoadlineOverlapModelViewSet(CustomModelViewSet):
    """
    公交线路复线情况管理
    提供标准的 CRUD 接口
    """
    
    queryset = RoadlineToRoadlineOverlapModel.objects.all()
    serializer_class = RoadlineToRoadlineOverlapSerializer
    create_serializer_class = RoadlineToRoadlineOverlapCreateSerializer
    update_serializer_class = RoadlineToRoadlineOverlapUpdateSerializer
    list_serializer_class = RoadlineToRoadlineOverlapListSerializer
    search_fields = ['main_roadline_code', 'main_roadline_name', 'vice_roadline_code', 'vice_roadline_name']
    ordering = ['-create_datetime']
