from apps.core.models import Task
from apps.core.serializers import TaskSerializer
from apps.core.views.base_view import BaseModelViewSet


class TaskViewSet(BaseModelViewSet):
    name = "task"
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all()
