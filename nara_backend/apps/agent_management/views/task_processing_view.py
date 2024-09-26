from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.agent_management.services.task_processor import TaskProcessor
from apps.core.models import Task


class TaskProcessingViewSet(viewsets.ViewSet):
    @action(detail=True, methods=["post"], url_path="process")
    def process_task(self, request, pk=None):
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({"error": "Task not found."}, status=status.HTTP_404_NOT_FOUND)

        processor = TaskProcessor()
        try:
            structured_output = processor.process(task)
            return Response(structured_output, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
