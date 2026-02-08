'''
Description: 上刊订单明细路由配置
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''

from rest_framework.routers import SimpleRouter
from .views import OnAirOrderDetailModelViewSet

router = SimpleRouter()
# 注册路径,并把视图关联上,这里的api地址以视图名称为后缀,这样方便记忆api/OnAirOrderDetailModelViewSet
router.register("api/OnAirOrderDetailModelViewSet", OnAirOrderDetailModelViewSet)

urlpatterns = [
]
urlpatterns += router.urls
