'''
Description: 
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''
#backend/dvadmin_twodev/basedata/media_type_composition/urls.py

from rest_framework.routers import SimpleRouter

from .views import AdMediaTypeCompositionModelViewSet

router = SimpleRouter()
# 这里进行注册路径，并把视图关联上，这里的api地址以视图名称为后缀，这样方便记忆api/AdMediaTypeCompositionModelViewSet
router.register("api/AdMediaTypeCompositionModelViewSet", AdMediaTypeCompositionModelViewSet)

urlpatterns = [
]
urlpatterns += router.urls

