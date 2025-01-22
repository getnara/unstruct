from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from apps.core.models.transformation_template import TransformationTemplate
from apps.core.serializers.transformation_template_serializer import TransformationTemplateSerializer

class TransformationTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for transformation templates.
    These templates are available to all users without authentication.
    """
    queryset = TransformationTemplate.objects.all()
    serializer_class = TransformationTemplateSerializer
    permission_classes = [AllowAny]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        template_type = self.request.query_params.get('template_type', None)
        if template_type:
            queryset = queryset.filter(template_type=template_type)
        return queryset

    @action(detail=True, methods=['get'])
    def actions(self, request, pk=None):
        """Get actions for a specific template"""
        template = self.get_object()
        serializer = self.get_serializer(template)
        return Response(serializer.data) 