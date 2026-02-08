'''
Description: 环域信息路由配置
Version: 1.0
Author: CursorAgent
Date: 2025-11-10 00:00:00
LastEditors: CursorAgent
LastEditTime: 2025-11-10 00:00:00
'''
from rest_framework.routers import SimpleRouter

from .views import DcBaseTorusinfoModelViewSet

router = SimpleRouter()
router.register("api/DcBaseTorusinfoModelViewSet", DcBaseTorusinfoModelViewSet)

urlpatterns = []
urlpatterns += router.urls

