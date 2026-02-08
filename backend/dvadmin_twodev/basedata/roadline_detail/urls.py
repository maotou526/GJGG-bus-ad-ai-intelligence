'''
Description: 线路走向详情路由配置
Version: 1.0
Autor: 王晨
Date: 2025-10-14
LastEditors: 王晨
LastEditTime: 2025-10-14
'''
#backend/basedata/roadline_detail/urls.py

from rest_framework.routers import SimpleRouter

from .views import RoadlineDetailViewSet

router = SimpleRouter()
# 这里进行注册路径，并把视图关联上，这里的api地址以视图名称为后缀，这样方便记忆api/RoadlineDetailViewSet
router.register("api/RoadlineDetailViewSet", RoadlineDetailViewSet)

urlpatterns = [
]
urlpatterns += router.urls

