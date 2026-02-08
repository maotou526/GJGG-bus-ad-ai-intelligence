'''
Description: 流程进程URL路由配置
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework.routers import SimpleRouter
from .views import WorkflowProcessModelViewSet

router = SimpleRouter()

# 注册视图集
# API地址格式：api/node_workflow/process/
router.register("api/node_workflow/process", WorkflowProcessModelViewSet, basename='workflow-process')

urlpatterns = []
urlpatterns += router.urls

