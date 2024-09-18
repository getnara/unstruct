from apps.core.models import Project
from apps.core.serializers import ProjectSerializer
from apps.core.views.base_view import BaseModelViewSet


class ProjectViewSet(BaseModelViewSet):
    name = "project"
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.all()
