"""
AI审核反馈URL配置
Description: AI审核反馈的路由配置
Version: 1.0
Date: 2026-02-03
"""
from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import AIAuditFeedbackViewSet

# 创建路由器
router = SimpleRouter()
router.register("api/AIAuditFeedbackViewSet", AIAuditFeedbackViewSet)

urlpatterns = []

urlpatterns += router.urls
