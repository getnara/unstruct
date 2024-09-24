from apps.common.views import NBaselViewSet
from apps.core.models import Project
from apps.core.serializers import ProjectSerializer


class ProjectViewSet(NBaselViewSet):
    name = "project"
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.all()
