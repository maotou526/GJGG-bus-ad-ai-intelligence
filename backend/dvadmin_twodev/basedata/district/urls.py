'''
Description: 
Version: 1.0
Autor: 王晨
Date: 2025-10-10 10:17:09
LastEditors: 王晨
LastEditTime: 2025-10-10 10:17:38
'''
#backend/crud_demo/urls.py

from rest_framework.routers import SimpleRouter

from .views import DistrictModelViewSet

router = SimpleRouter()
# 这里进行注册路径，并把视图关联上，这里的api地址以视图名称为后缀，这样方便记忆api/CrudDemoModelViewSet
router.register("api/DistrictModelViewSet", DistrictModelViewSet)

urlpatterns = [
]
urlpatterns += router.urls