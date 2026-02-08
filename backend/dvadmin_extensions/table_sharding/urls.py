'''
Description: 分表管理路由配置
Version: 1.0
Author: 王晨
Date: 2025-11-26
LastEditors: 王晨
LastEditTime: 2025-11-26
'''
from rest_framework.routers import SimpleRouter
from .views import TableShardingViewSet

router = SimpleRouter()

# 注册视图集
router.register(r'', TableShardingViewSet, basename='table_sharding')

urlpatterns = router.urls

