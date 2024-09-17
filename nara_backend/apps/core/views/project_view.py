from rest_framework import viewsets

from apps.core.models import Project
from apps.core.serializers import ProjectSerializer


class ProjectViewSet(viewsets.ModelViewSet):
    name = "project"
    serializer_class = ProjectSerializer

    def get_queryset(self):
        return Project.objects.all()
