from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.request import Request
from rest_framework import status

class ApiRoot(APIView):
    """
    API root view that provides links to all available endpoints.
    """
    name = "api-root"
    
    def get(self, request: Request, format=None) -> Response:
        return Response({
            'projects': reverse('project-list', request=request, format=format),
            'assets': reverse('asset-list', request=request, format=format),
            'actions': reverse('action-list', request=request, format=format),
            'tasks': reverse('task-list', request=request, format=format),
            'users': reverse('user-list', request=request, format=format),
            'organizations': reverse('organization-list', request=request, format=format),
        })

class HealthCheckView(APIView):
    """
    Simple health check endpoint to verify the API is running.
    """
    def get(self, request: Request, format=None) -> Response:
        return Response({"status": "healthy"}, status=status.HTTP_200_OK)
