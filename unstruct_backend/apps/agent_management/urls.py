from rest_framework import routers

from apps.agent_management.views import ModelConfigurationViewSet, TaskProcessingViewSet

urlpatterns = []

router = routers.SimpleRouter()
router.register(ModelConfigurationViewSet.name, ModelConfigurationViewSet, basename=ModelConfigurationViewSet.name)
router.register('tasks', TaskProcessingViewSet, basename=TaskProcessingViewSet.name)
urlpatterns += router.urls
