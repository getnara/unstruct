from apps.core.models import Action
from apps.core.serializers import ActionSerializer
from apps.core.views.base_view import BaseModelViewSet


class ActionViewSet(BaseModelViewSet):
    name = "action"
    serializer_class = ActionSerializer

    def get_queryset(self):
        return Action.objects.all()
