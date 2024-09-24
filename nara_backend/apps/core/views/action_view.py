from apps.common.views import NBaselViewSet
from apps.core.models import Action
from apps.core.serializers import ActionSerializer


class ActionViewSet(NBaselViewSet):
    name = "action"
    serializer_class = ActionSerializer

    def get_queryset(self):
        return Action.objects.all()
