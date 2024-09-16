from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.reverse import reverse

from apps.core.models import Action, Asset, Project, Task
from apps.core.serializers import (
    ActionSerializer,
    AssetSerializer,
    ProjectSerializer,
    TaskSerializer,
)


class ApiRoot(generics.GenericAPIView):
    name = "api-root"

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "projects": reverse(ProjectList.name, request=request),
                "assets": reverse(AssetList.name, request=request),
                "actions": reverse(ActionList.name, request=request),
                "tasks": reverse(TaskList.name, request=request),
            }
        )


class ProjectList(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    name = "project-list"


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    name = "project-detail"


class AssetList(generics.ListCreateAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    name = "asset-list"


class AssetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    name = "asset-detail"


class ActionList(generics.ListCreateAPIView):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    name = "action-list"


class ActionDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Action.objects.all()
    serializer_class = ActionSerializer
    name = "action-detail"


class TaskList(generics.ListCreateAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    name = "task-list"


class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    name = "task-detail"
