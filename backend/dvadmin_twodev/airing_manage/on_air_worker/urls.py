"""
Description: 上刊施工人员路由配置
Version: 1.0
"""
from rest_framework.routers import SimpleRouter
from .views import OnAirWorkerModelViewSet

router = SimpleRouter()
router.register("api/OnAirWorkerModelViewSet", OnAirWorkerModelViewSet)

urlpatterns = [
]
urlpatterns += router.urls
