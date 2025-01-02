from django.urls import path
from rest_framework import routers

from apps.core.views import (
    ActionViewSet, AssetViewSet, ProjectViewSet, TaskViewSet, UserViewSet,
    GoogleDriveFilesView, GoogleDriveAuthView, GoogleDriveCallbackView, OrganizationViewSet,
    HealthCheckView
)

urlpatterns = [
    path('health/', HealthCheckView.as_view(), name='health_check'),
    path('google-drive/files/', GoogleDriveFilesView.as_view(), name='google_drive_files'),
    path('google-drive/auth/', GoogleDriveAuthView.as_view(), name='google_drive_auth'),
    path('google-drive/callback/', GoogleDriveCallbackView.as_view(), name='google_drive_callback'),
]

router = routers.SimpleRouter()
router.register(ProjectViewSet.name, ProjectViewSet, basename=ProjectViewSet.name)
router.register(AssetViewSet.name, AssetViewSet, basename=AssetViewSet.name)
router.register(ActionViewSet.name, ActionViewSet, basename=ActionViewSet.name)
router.register(TaskViewSet.name, TaskViewSet, basename=TaskViewSet.name)
router.register(UserViewSet.name, UserViewSet, basename=UserViewSet.name)
router.register(OrganizationViewSet.name, OrganizationViewSet, basename=OrganizationViewSet.name)

urlpatterns = urlpatterns + router.urls
