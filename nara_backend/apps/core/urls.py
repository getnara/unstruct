from django.urls import path
from rest_framework import routers

from apps.core.views import (
    ActionViewSet,
    ApiRoot,
    AssetViewSet,
    CognitoLoginView,
    ProjectViewSet,
    TaskViewSet,
    UserViewSet,
)

urlpatterns = [
    path("dj-rest-auth/cognito/", CognitoLoginView.as_view(), name="cognito_login"),
    path("", ApiRoot.as_view(), name=ApiRoot.name),
]

router = routers.SimpleRouter()
router.register(ProjectViewSet.name, ProjectViewSet, basename=ProjectViewSet.name)
router.register(AssetViewSet.name, AssetViewSet, basename=AssetViewSet.name)
router.register(ActionViewSet.name, ActionViewSet, basename=ActionViewSet.name)
router.register(TaskViewSet.name, TaskViewSet, basename=TaskViewSet.name)
router.register(UserViewSet.name, UserViewSet, basename=UserViewSet.name)

urlpatterns += router.urls
