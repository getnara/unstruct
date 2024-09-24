from apps.common.serializers import NBaseSerializer
from apps.core.models import Task


class TaskSerializer(NBaseSerializer):
    class Meta:
        model = Task
        fields = "__all__"
