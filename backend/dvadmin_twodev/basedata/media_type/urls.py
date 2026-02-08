'''
Description: 
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
#backend/dvadmin_twodev/basedata/media_type/urls.py

from rest_framework.routers import SimpleRouter

from .views import AdMediaTypeModelViewSet

router = SimpleRouter()
# 这里进行注册路径，并把视图关联上，这里的api地址以视图名称为后缀，这样方便记忆api/AdMediaTypeModelViewSet
router.register("api/AdMediaTypeModelViewSet", AdMediaTypeModelViewSet)

urlpatterns = [
]
urlpatterns += router.urls

