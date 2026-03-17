"""
Description: 上刊施工文件路由配置
Version: 1.0
"""
from rest_framework.routers import SimpleRouter
from .views import OnAirFileModelViewSet

router = SimpleRouter()
router.register("api/OnAirFileModelViewSet", OnAirFileModelViewSet)

urlpatterns = [
]
urlpatterns += router.urls
