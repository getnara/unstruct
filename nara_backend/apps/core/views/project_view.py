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

    def perform_create(self, serializer):
        # First call the parent's perform_create to set organization and created_by/updated_by
        super().perform_create(serializer)
        # Then update the instance to set the owner
        instance = serializer.instance
        instance.owner = self.request.user
        instance.save()

    def list(self, request, *args, **kwargs):
        timings = []
        
        with ViewTimingContextManager("query_projects") as timing:
            queryset = self.get_queryset()
            queryset = queryset.prefetch_related('collaborators', 'assets', 'tasks')
            if hasattr(timing, 'duration') and timing.duration is not None:
                timings.append(f"query_projects;dur={timing.duration:.2f};desc='Query Projects'")
            else:
                timings.append("query_projects;dur=0;desc='Query Projects'")
        
        with ViewTimingContextManager("serialize_projects") as timing:
            serializer = self.get_serializer(queryset, many=True)
            if hasattr(timing, 'duration') and timing.duration is not None:
                timings.append(f"serialize_projects;dur={timing.duration:.2f};desc='Serialize Projects'")
            else:
                timings.append("serialize_projects;dur=0;desc='Serialize Projects'")
        
        response = Response(serializer.data)
        response["Server-Timing"] = ", ".join(timings)
        return response

    def retrieve(self, request, *args, **kwargs):
        timings = []
        
        with ViewTimingContextManager("query_project") as timing:
            instance = self.get_object()
            instance = self.get_queryset().prefetch_related(
                'collaborators',
                'assets',
                'tasks'
            ).get(id=instance.id)
            if hasattr(timing, 'duration') and timing.duration is not None:
                timings.append(f"query_project;dur={timing.duration:.2f};desc='Query Project'")
            else:
                timings.append("query_project;dur=0;desc='Query Project'")
        
        with ViewTimingContextManager("serialize_project") as timing:
            serializer = self.get_serializer(instance)
            if hasattr(timing, 'duration') and timing.duration is not None:
                timings.append(f"serialize_project;dur={timing.duration:.2f};desc='Serialize Project'")
            else:
                timings.append("serialize_project;dur=0;desc='Serialize Project'")
        
        with ViewTimingContextManager("count_related") as timing:
            related_counts = {
                'collaborators_count': instance.collaborators.count(),
                'assets_count': instance.assets.count(),
                'tasks_count': instance.tasks.count(),
            }
            if hasattr(timing, 'duration') and timing.duration is not None:
                timings.append(f"count_related;dur={timing.duration:.2f};desc='Count Related Objects'")
            else:
                timings.append("count_related;dur=0;desc='Count Related Objects'")
        
        response_data = {
            **serializer.data,
            **related_counts
        }
        
        response = Response(response_data)
        response["Server-Timing"] = ", ".join(timings)
        return response