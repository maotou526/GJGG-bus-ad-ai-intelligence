'''
Description: 站点关联路由配置
Version: 1.0
Autor: 王晨
Date: 2025-10-14
LastEditors: 王晨
LastEditTime: 2025-10-14
'''

from rest_framework.routers import SimpleRouter

from .views import RoadlineStopRelModelViewSet

router = SimpleRouter()
# 注册路径，并把视图关联上
router.register("api/RoadlineStopRelModelViewSet", RoadlineStopRelModelViewSet)

urlpatterns = [
]
urlpatterns += router.urls