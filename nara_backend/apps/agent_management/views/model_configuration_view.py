from apps.agent_management.models import ModelConfiguration
from apps.agent_management.serializers import ModelConfigurationSerializer
from apps.common.views import NBaselViewSet


class ModelConfigurationViewSet(NBaselViewSet):
    name = "model_configuration"
    serializer_class = ModelConfigurationSerializer

    def get_queryset(self):
        return ModelConfiguration.objects.all()
