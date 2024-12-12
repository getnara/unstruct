from rest_framework import routers

from apps.core.views import (
    ActionViewSet,
    AssetViewSet,
    ProjectViewSet,
    TaskViewSet,
    UserViewSet,
    OrganizationViewSet
)

router = routers.SimpleRouter()
router.register(ProjectViewSet.name, ProjectViewSet, basename=ProjectViewSet.name)
router.register(AssetViewSet.name, AssetViewSet, basename=AssetViewSet.name)
router.register(ActionViewSet.name, ActionViewSet, basename=ActionViewSet.name)
router.register(TaskViewSet.name, TaskViewSet, basename=TaskViewSet.name)
router.register(UserViewSet.name, UserViewSet, basename=UserViewSet.name)
router.register(OrganizationViewSet.name, OrganizationViewSet, basename=OrganizationViewSet.name)

urlpatterns = router.urls
