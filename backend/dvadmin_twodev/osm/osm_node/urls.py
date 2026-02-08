from rest_framework.routers import SimpleRouter
from .views import OsmNodeModelViewSet

router = SimpleRouter()
router.register("api/OsmNodeModelViewSet", OsmNodeModelViewSet)

urlpatterns = []
urlpatterns += router.urls

