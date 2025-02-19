from apps.common.views import NBaselViewSet
from apps.core.models import Action
from apps.core.serializers import ActionSerializer
from apps.common.mixins.organization_mixin import OrganizationMixin


class ActionViewSet(OrganizationMixin, NBaselViewSet):
    name = "action"
    serializer_class = ActionSerializer
    queryset = Action.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(organization=self.get_organization())
