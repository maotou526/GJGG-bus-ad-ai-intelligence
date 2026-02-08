'''
Description: 地图查询管理路由配置
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''

from rest_framework.routers import SimpleRouter
from .views import MapManageModelViewSet

router = SimpleRouter()
# 注册路径，并把视图关联上
router.register("api/MapManageModelViewSet", MapManageModelViewSet)

urlpatterns = []
urlpatterns += router.urls
