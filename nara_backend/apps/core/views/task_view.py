from rest_framework import viewsets

from apps.core.models import Task
from apps.core.serializers import TaskSerializer


class TaskViewSet(viewsets.ModelViewSet):
    name = "task"
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all()
