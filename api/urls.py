from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(prefix="parents", viewset=views.ParentViewSet, basename="parents")
router.register(prefix="students", viewset=views.StudentViewSet, basename="students")
router.register(prefix="teachers", viewset=views.TeacherViewSet, basename="teachers")
router.register(prefix="groups", viewset=views.GroupViewSet, basename="groups")
router.register(prefix="subjects", viewset=views.SubjectViewSet, basename="subjects")
router.register(prefix="rooms", viewset=views.RoomViewSet, basename="rooms")
router.register(prefix="admins", viewset=views.AdminViewSet, basename="admins")
router.register(prefix="superusers", viewset=views.SuperuserViewSet, basename="superusers")

urlpatterns = router.urls
