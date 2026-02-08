"""
Description: 消息通知URL路由
Version: 1.0
Autor: AI Assistant
Date: 2026-02-05
LastEditors: 
LastEditTime: 2026-02-05
"""
from rest_framework import routers
from django.urls import path
from .views import NoticeModelViewSet, NoticeUserModelViewSet

router = routers.SimpleRouter()
router.register(r'notice', NoticeModelViewSet, basename='notice')
router.register(r'notice_user', NoticeUserModelViewSet, basename='notice_user')

urlpatterns = router.urls

