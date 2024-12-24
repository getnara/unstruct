from rest_framework.response import Response
from apps.common.views import NBaselViewSet
from apps.core.models import Project
from apps.core.serializers import ProjectSerializer
from apps.common.middleware.timing_middleware import ViewTimingContextManager
from apps.common.mixins.organization_mixin import OrganizationMixin


class ProjectViewSet(OrganizationMixin, NBaselViewSet):
    name = "project"
    serializer_class = ProjectSerializer
    queryset = Project.objects.all()

    def get_queryset(self):
        return super().get_queryset().filter(organization=self.get_organization())

    def list(self, request, *args, **kwargs):
        timings = []
        
        with ViewTimingContextManager("query_projects") as timing:
            queryset = self.get_queryset()
            # Prefetch related data to optimize performance
            queryset = queryset.prefetch_related('collaborators', 'assets', 'tasks')
            timings.append(f"query_projects;dur={timing.duration:.2f};desc='Query Projects'")
        
        with ViewTimingContextManager("serialize_projects") as timing:
            serializer = self.get_serializer(queryset, many=True)
            timings.append(f"serialize_projects;dur={timing.duration:.2f};desc='Serialize Projects'")
        
        response = Response(serializer.data)
        response["Server-Timing"] = ", ".join(timings)
        return response

    def retrieve(self, request, *args, **kwargs):
        timings = []
        
        with ViewTimingContextManager("query_project") as timing:
            instance = self.get_object()
            # Prefetch related data
            instance = self.get_queryset().prefetch_related(
                'collaborators',
                'assets',
                'tasks'
            ).get(id=instance.id)
            timings.append(f"query_project;dur={timing.duration:.2f};desc='Query Project'")
        
        with ViewTimingContextManager("serialize_project") as timing:
            serializer = self.get_serializer(instance)
            timings.append(f"serialize_project;dur={timing.duration:.2f};desc='Serialize Project'")
        
        with ViewTimingContextManager("count_related") as timing:
            # Get counts for related objects
            related_counts = {
                'collaborators_count': instance.collaborators.count(),
                'assets_count': instance.assets.count(),
                'tasks_count': instance.tasks.count(),
            }
            timings.append(f"count_related;dur={timing.duration:.2f};desc='Count Related Objects'")
        
        response_data = {
            **serializer.data,
            **related_counts
        }
        
        response = Response(response_data)
        response["Server-Timing"] = ", ".join(timings)
        return response
