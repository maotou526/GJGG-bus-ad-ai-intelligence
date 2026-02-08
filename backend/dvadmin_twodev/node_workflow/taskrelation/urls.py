'''
Description: 任务执行人关系URL路由配置
Version: 1.0
Author: System
Date: 2025-01-14
LastEditors: 
LastEditTime: 
'''
from rest_framework.routers import SimpleRouter
from .views import WorkflowTaskRelationModelViewSet

router = SimpleRouter()

# 注册视图集
# API地址格式：api/node_workflow/taskrelation/
router.register("api/node_workflow/taskrelation", WorkflowTaskRelationModelViewSet, basename='workflow-taskrelation')

urlpatterns = []
urlpatterns += router.urls

