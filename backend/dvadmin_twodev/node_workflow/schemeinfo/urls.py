'''
Description: 流程模板信息URL路由配置
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework.routers import SimpleRouter
from .views import WorkflowSchemeInfoModelViewSet

router = SimpleRouter()

# 注册视图集
# API地址格式：api/node_workflow/schemeinfo/
router.register("api/node_workflow/schemeinfo", WorkflowSchemeInfoModelViewSet, basename='workflow-schemeinfo')

urlpatterns = []
urlpatterns += router.urls

