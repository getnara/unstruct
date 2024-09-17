from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse


class ApiRoot(generics.GenericAPIView):
    name = "api-root"

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "users": reverse("user-list", request=request),
                "projects": reverse("project-list", request=request),
                "assets": reverse("asset-list", request=request),
                "actions": reverse("action-list", request=request),
                "tasks": reverse("task-list", request=request),
            }
        )
