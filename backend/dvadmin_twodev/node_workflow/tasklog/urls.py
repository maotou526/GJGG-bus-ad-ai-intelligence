'''
Description: 任务日志URL路由配置
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework.routers import SimpleRouter
from .views import WorkflowTaskLogModelViewSet

router = SimpleRouter()

# 注册视图集
# API地址格式：api/node_workflow/tasklog/
router.register("api/node_workflow/tasklog", WorkflowTaskLogModelViewSet, basename='workflow-tasklog')

urlpatterns = []
urlpatterns += router.urls

