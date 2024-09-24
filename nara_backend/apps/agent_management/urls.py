from rest_framework import routers

from apps.agent_management.views import ModelConfigurationViewSet

urlpatterns = []

router = routers.SimpleRouter()
router.register(ModelConfigurationViewSet.name, ModelConfigurationViewSet, basename=ModelConfigurationViewSet.name)

urlpatterns += router.urls
