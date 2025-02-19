from apps.common.serializers import NBaseSerializer
from apps.core.models import Project


class ProjectSerializer(NBaseSerializer):
    class Meta:
        model = Project
        fields = "__all__"
