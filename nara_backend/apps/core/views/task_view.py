from apps.common.views import NBaselViewSet
from apps.core.models import Task
from apps.core.serializers import TaskSerializer


class TaskViewSet(NBaselViewSet):
    name = "task"
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all()
