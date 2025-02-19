from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.db.models import Q
from apps.core.models.transformation_template import TransformationTemplate
from apps.core.serializers.transformation_template_serializer import TransformationTemplateSerializer
from apps.common.mixins.organization_mixin import OrganizationMixin

class TransformationTemplateViewSet(OrganizationMixin, viewsets.ModelViewSet):
    """
    ViewSet for transformation templates.
    List and retrieve actions are available to all users.
    Create, update and delete actions require authentication.
    Templates can be organization-specific or global.
    """
    serializer_class = TransformationTemplateSerializer
    
    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'actions']:
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = TransformationTemplate.objects.filter(
            Q(is_global=True) |  # Global templates
            Q(organization=self.get_organization())  # Organization-specific templates
        )
        
        template_type = self.request.query_params.get('template_type', None)
        if template_type:
            queryset = queryset.filter(template_type=template_type)
            
        return queryset

    def perform_create(self, serializer):
        """Create a new template for the organization"""
        organization = self.get_organization()
        serializer.save(
            organization=organization,
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        """Update the template"""
        serializer.save(updated_by=self.request.user)

    @action(detail=True, methods=['get'])
    def actions(self, request, pk=None):
        """Get actions for a specific template"""
        template = self.get_object()
        serializer = self.get_serializer(template)
        return Response(serializer.data) 