"""
数据权限扩展路由配置
"""
from django.urls import path
from rest_framework.routers import SimpleRouter
from .views import DataPermissionRuleViewSet

# 创建路由
router = SimpleRouter()
router.register(r'data_permission_rule', DataPermissionRuleViewSet, basename='data_permission_rule')

urlpatterns = router.urls

