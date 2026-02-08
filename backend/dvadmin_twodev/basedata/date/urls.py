'''
Description: 
Version: 1.0
Autor: 王晨
Date: 2025-10-23
LastEditors: 王晨
LastEditTime: 2025-10-23
'''

from rest_framework.routers import SimpleRouter

from .views import BaseDateModelViewSet

router = SimpleRouter()
router.register("api/BaseDateModelViewSet", BaseDateModelViewSet)

urlpatterns = [
]
urlpatterns += router.urls

