'''
Description: 任务消息URL路由配置
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework.routers import SimpleRouter
from .views import WorkflowTaskMsgModelViewSet

router = SimpleRouter()

# 注册视图集
# API地址格式：api/node_workflow/taskmsg/
router.register("api/node_workflow/taskmsg", WorkflowTaskMsgModelViewSet, basename='workflow-taskmsg')

urlpatterns = []
urlpatterns += router.urls

