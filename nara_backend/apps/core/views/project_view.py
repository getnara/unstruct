from apps.common.views import NBaselViewSet
from apps.common.mixins.organization_mixin import OrganizationMixin
from apps.core.models import Project
from apps.core.serializers import ProjectSerializer


class ProjectViewSet(OrganizationMixin, NBaselViewSet):
    name = "project"
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(organization=self.get_organization())
