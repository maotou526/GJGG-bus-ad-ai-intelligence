'''
Description: 公交线路复线情况URL路由配置
Version: 1.0
Author: 王晨
Date: 2025-01-XX
LastEditors: 
LastEditTime: 
'''
from rest_framework.routers import SimpleRouter
from .views import RoadlineToRoadlineOverlapModelViewSet

router = SimpleRouter()
router.register("api/RoadlineToRoadlineOverlapModelViewSet", RoadlineToRoadlineOverlapModelViewSet)

urlpatterns = []
urlpatterns += router.urls

