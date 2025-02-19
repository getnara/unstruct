from rest_framework import permissions
from apps.core.models.organization import Organization, OrganizationMember


class IsOrganizationAdmin(permissions.BasePermission):
    """
    Permission check for organization admin access.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Get the organization based on the view's get_object
        if isinstance(obj, Organization):
            organization = obj
        elif isinstance(obj, OrganizationMember):
            organization = obj.organization
        else:
            # For other cases, try to get organization from the URL
            try:
                organization_id = view.kwargs.get('pk')
                organization = Organization.objects.get(id=organization_id)
            except Organization.DoesNotExist:
                return False
            
        # Check if user is organization owner
        if organization.owner == request.user:
            return True
            
        # Check if user is an admin member
        return organization.members.filter(
            user=request.user,
            role='admin',
            invitation_accepted=True
        ).exists()
