from django.urls import path

from apps.core.views import (
    ActionDetail,
    ActionList,
    ApiRoot,
    AssetDetail,
    AssetList,
    CognitoLoginView,
    ProjectDetail,
    ProjectList,
    TaskDetail,
    TaskList,
)

urlpatterns = [
    path("dj-rest-auth/cognito/", CognitoLoginView.as_view(), name="cognito_login"),
    path("project/", ProjectList.as_view(), name=ProjectList.name),
    path("project/<int:pk>/", ProjectDetail.as_view(), name=ProjectDetail.name),
    path("task/", TaskList.as_view(), name=TaskList.name),
    path("task/<int:pk>/", TaskDetail.as_view(), name=TaskDetail.name),
    path("action/", ActionList.as_view(), name=ActionList.name),
    path("action/<int:pk>/", ActionDetail.as_view(), name=ActionDetail.name),
    path("asset/", AssetList.as_view(), name=AssetList.name),
    path("asset/<int:pk>/", AssetDetail.as_view(), name=AssetDetail.name),
    path("", ApiRoot.as_view(), name=ApiRoot.name),
]
