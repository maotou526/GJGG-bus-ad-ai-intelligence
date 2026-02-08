'''
Description: 代理商路由配置
Version: 1.0
Autor: AI Assistant
Date: 2025-01-XX
LastEditors: 
LastEditTime: 2025-01-XX
'''

from rest_framework.routers import SimpleRouter
from .views import AgentModelViewSet

router = SimpleRouter()
# 注册路径,并把视图关联上,这里的api地址以视图名称为后缀,这样方便记忆api/AgentModelViewSet
router.register("api/AgentModelViewSet", AgentModelViewSet)

urlpatterns = [
]
urlpatterns += router.urls

