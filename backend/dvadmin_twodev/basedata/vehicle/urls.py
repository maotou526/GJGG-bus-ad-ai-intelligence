'''
Description: 车辆路由配置
Version: 1.0
Autor: 王晨
Date: 2025-10-18
LastEditors: 王晨
LastEditTime: 2025-10-18
'''

from rest_framework.routers import SimpleRouter
from .views import VehicleModelViewSet

router = SimpleRouter()
# 注册路径,并把视图关联上,这里的api地址以视图名称为后缀,这样方便记忆api/VehicleModelViewSet
router.register("api/VehicleModelViewSet", VehicleModelViewSet)

urlpatterns = [
]
urlpatterns += router.urls

