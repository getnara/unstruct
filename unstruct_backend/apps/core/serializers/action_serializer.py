from apps.common.serializers import NBaseSerializer
from apps.core.models import Action


class ActionSerializer(NBaseSerializer):
    class Meta:
        model = Action
        fields = "__all__"
