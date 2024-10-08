from apps.common.views import NBaselViewSet
from apps.core.models import Task
from apps.core.serializers import TaskSerializer
from apps.agent_management.services.task_processor import TaskProcessor
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response


class TaskViewSet(NBaselViewSet):
    name = "task"
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.all()
    
    @action(detail=False, methods=["post"], url_path="process")
    def process_task(self, request):
        try:
            task_id = request.data.get("task_id")
            task = Task.objects.get(pk=task_id)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        processor = TaskProcessor()
        try:
            structured_output = processor.process(task)
            return Response(structured_output, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
