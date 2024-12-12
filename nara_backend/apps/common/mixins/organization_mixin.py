from rest_framework import status
from rest_framework.exceptions import ValidationError, PermissionDenied
from apps.core.models.organization import Organization


class OrganizationMixin:
    def get_organization(self):
        org_id = self.request.headers.get("X-Organization-ID")
        if not org_id:
            # If no org ID provided, try to get personal organization
            personal_org = Organization.objects.filter(
                name="personal",
                owner=self.request.user
            ).first()
            if not personal_org:
                raise ValidationError(
                    "No organization ID provided and no personal organization found",
                    code=status.HTTP_400_BAD_REQUEST
                )
            return personal_org

        try:
            org = Organization.objects.get(id=org_id)
        except Organization.DoesNotExist:
            raise ValidationError(
                f"Organization with ID {org_id} does not exist",
                code=status.HTTP_404_NOT_FOUND
            )

        # Check if user has access to this organization
        if not org.has_member(self.request.user):
            raise ValidationError(
                f"You do not have access to organization {org_id}",
                code=status.HTTP_403_FORBIDDEN
            )

        return org

    def get_queryset(self):
        queryset = super().get_queryset()
        organization = self.get_organization()
        return queryset.filter(organization=organization)

    def perform_create(self, serializer):
        organization = self.get_organization()
        serializer.save(
            organization=organization,
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
