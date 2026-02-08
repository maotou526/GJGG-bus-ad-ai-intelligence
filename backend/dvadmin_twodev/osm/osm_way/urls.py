from rest_framework.routers import SimpleRouter
from .views import OsmWayModelViewSet

router = SimpleRouter()
router.register("api/OsmWayModelViewSet", OsmWayModelViewSet)

urlpatterns = []
urlpatterns += router.urls

