from rest_framework.routers import SimpleRouter
from .views import OsmNodeWayRelModelViewSet

router = SimpleRouter()
router.register("api/OsmNodeWayRelModelViewSet", OsmNodeWayRelModelViewSet)

urlpatterns = []
urlpatterns += router.urls

