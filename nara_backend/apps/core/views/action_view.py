from rest_framework import viewsets

from apps.core.models import Action
from apps.core.serializers import ActionSerializer


class ActionViewSet(viewsets.ModelViewSet):
    name = "action"
    serializer_class = ActionSerializer

    def get_queryset(self):
        return Action.objects.all()
