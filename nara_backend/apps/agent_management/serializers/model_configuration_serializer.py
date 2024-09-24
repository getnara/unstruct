from apps.agent_management.models import ModelConfiguration
from apps.common.serializers import NBaseSerializer


class ModelConfigurationSerializer(NBaseSerializer):
    class Meta:
        model = ModelConfiguration
        fields = "__all__"
