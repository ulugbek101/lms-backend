from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(prefix="users", viewset=views.StaffViewSet, basename="users")

urlpatterns = router.urls
