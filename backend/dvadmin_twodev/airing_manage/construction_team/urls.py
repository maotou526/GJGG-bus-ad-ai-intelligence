'''
Description: 施工团队路由配置
Version: 1.0
Autor: AI Assistant
Date: 2026-03-17
LastEditors:
LastEditTime: 2026-03-17
'''

from rest_framework.routers import SimpleRouter
from .views import ConstructionTeamModelViewSet

router = SimpleRouter()
# 注册路径,并把视图关联上,这里的api地址以视图名称为后缀,这样方便记忆api/ConstructionTeamModelViewSet
router.register("api/ConstructionTeamModelViewSet", ConstructionTeamModelViewSet)

urlpatterns = [
]
urlpatterns += router.urls
