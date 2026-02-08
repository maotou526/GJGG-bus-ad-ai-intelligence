'''
Description: 车型管理路由
'''
from rest_framework.routers import SimpleRouter
from .views import VehicleTypeModelViewSet

router = SimpleRouter()
router.register("api/VehicleTypeModelViewSet", VehicleTypeModelViewSet)

urlpatterns = []
urlpatterns += router.urls

