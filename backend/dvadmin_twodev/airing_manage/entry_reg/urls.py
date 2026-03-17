"""
Description: 进场登记路由配置
Version: 1.0
"""
from rest_framework.routers import SimpleRouter
from .views import EntryRegModelViewSet

router = SimpleRouter()
router.register("api/EntryRegModelViewSet", EntryRegModelViewSet)

urlpatterns = [
]
urlpatterns += router.urls
