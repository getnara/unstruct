from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
import logging
from django.db.models import Q
from django.core.exceptions import ValidationError

from apps.core.models.organization import Organization, OrganizationMember
from apps.core.models.user import User
from apps.core.permissions import IsOrganizationAdmin
from apps.core.serializers.organization_serializer import (
    OrganizationSerializer,
    OrganizationMemberSerializer,
    OrganizationInviteSerializer
)
from apps.common.views import NBaselViewSet

logger = logging.getLogger(__name__)

class OrganizationViewSet(NBaselViewSet):
    name = "organizations"
    serializer_class = OrganizationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Get organizations where the user is an owner or an accepted member.
        """
        user = self.request.user
        return Organization.objects.filter(
            Q(owner=user) |  # User is owner
            Q(members__user=user, members__invitation_accepted=True)  # User is accepted member
        ).distinct()

    def perform_create(self, serializer):
        try:
            # Check if user can create more organizations
            Organization.can_create_organization(self.request.user)
            
            # Create the organization
            organization = serializer.save(owner=self.request.user)
            
            # Create admin membership
            OrganizationMember.objects.create(
                organization=organization,
                user=self.request.user,
                role='admin',
                invitation_accepted=True
            )
        except ValidationError as e:
            # Delete the organization if it was created
            if 'organization' in locals():
                organization.delete()
            # Re-raise the error to be handled by the DRF exception handler
            raise ValidationError({
                "error": str(e)
            })

    @action(detail=True, methods=['post'], url_path='invite-member')
    def invite_member(self, request, pk=None):
        """Invite a member to the organization."""
        organization = self.get_object()
        serializer = OrganizationInviteSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            role = serializer.validated_data.get('role', 'member')

            try:
                # Get current member counts
                total_members = organization.members.count()
                accepted_members = organization.members.filter(invitation_accepted=True).count()
                pending_invites = organization.members.filter(invitation_accepted=False).count()
                
                print(f"Current member counts - Total: {total_members}, Accepted: {accepted_members}, Pending: {pending_invites}")
                
                # Check if we can add more members
                organization.can_add_member()

                # Check if member already exists in the organization (active or pending)
                existing_member = OrganizationMember.objects.filter(
                    organization=organization
                ).filter(
                    Q(invitation_email=email) | Q(user__email=email)
                ).first()

                if existing_member:
                    if existing_member.invitation_accepted:
                        return Response(
                            {"error": "User is already a member of this organization"},
                            status=status.HTTP_400_BAD_REQUEST
                        )
                    else:
                        return Response(
                            {"error": "An invitation is already pending for this user"},
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # Find if user exists
                user = User.objects.filter(email=email).first()
                
                # Create member with invitation_accepted=False for both existing and new users
                member = OrganizationMember.objects.create(
                    organization=organization,
                    user=user,
                    invitation_email=email,
                    role=role,
                    invitation_accepted=False  # Always require acceptance
                )

                try:
                    # Send invitation email
                    frontend_url = "http://localhost:3000"  # Default development frontend URL
                    invite_url = f"{frontend_url}/organizations/{organization.id}/accept-invite"
                    send_mail(
                        f'Invitation to join {organization.name}',
                        f'You have been invited to join {organization.name}. Click here to accept: {invite_url}',
                        settings.DEFAULT_FROM_EMAIL,
                        [email],
                        fail_silently=True,
                    )
                except Exception as e:
                    print(f"Failed to send invitation email: {str(e)}")

                return Response({
                    'id': member.id,
                    'invitation_email': member.invitation_email,
                    'role': member.role,
                    'invitation_accepted': member.invitation_accepted,
                    'member_counts': {
                        'total': total_members + 1,  # Including the new invite
                        'accepted': accepted_members,
                        'pending': pending_invites + 1  # Including the new invite
                    }
                })

            except ValidationError as e:
                return Response({
                    "error": str(e),
                    "member_counts": {
                        'total': total_members,
                        'accepted': accepted_members,
                        'pending': pending_invites
                    }
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        organization = self.get_object()
        members = OrganizationMember.objects.filter(organization=organization)
        serializer = OrganizationMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['delete'], url_path='members/(?P<member_id>[^/.]+)', permission_classes=[IsOrganizationAdmin])
    def remove_member(self, request, pk=None, member_id=None):
        """Remove a member from the organization. Only admins can perform this action."""
        try:
            organization = self.get_object()
            
            # Get the member and ensure it belongs to this organization
            member = get_object_or_404(OrganizationMember, id=member_id, organization=organization)
            
            # Don't allow removing the owner
            if member.user and member.user == organization.owner:
                return Response(
                    {"error": "Cannot remove the organization owner"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Delete the member
            member.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['get'], url_path='invitations')
    def list_invitations(self, request):
        """List all invitations for the current user."""
        # Get invitations by email or user, but not both
        invitations = OrganizationMember.objects.filter(
            Q(invitation_email=request.user.email) | Q(user=request.user),
            invitation_accepted=False
        ).select_related('organization', 'user').distinct()
        
        # Serialize the invitations with organization details
        data = []
        for invitation in invitations:
            data.append({
                'id': invitation.id,
                'organization': {
                    'id': invitation.organization.id,
                    'name': invitation.organization.name,
                    'description': invitation.organization.description,
                },
                'role': invitation.role,
                'created_at': invitation.created_at,
                'invitation_email': invitation.invitation_email,
                'user': {
                    'id': invitation.user.id,
                    'email': invitation.user.email,
                    'username': invitation.user.username
                } if invitation.user else None,
                'invitation_accepted': invitation.invitation_accepted
            })
        
        return Response(data)

    @action(detail=False, methods=['post'], url_path='(?P<invitation_id>[^/.]+)/accept-invite')
    def accept_invitation(self, request, invitation_id=None):
        """Accept an organization invitation using the invitation ID."""
        try:
            # Get the invitation directly using its ID
            member = get_object_or_404(OrganizationMember, id=invitation_id)
            
            # Verify the invitation belongs to the current user
            if member.user != request.user and member.invitation_email != request.user.email:
                return Response(
                    {"error": "This invitation does not belong to you"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Accept the invitation
            member.invitation_accepted = True
            member.user = request.user  # Ensure the user is set (for email invitations)
            member.save()
            
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='(?P<invitation_id>[^/.]+)/decline-invite')
    def decline_invitation(self, request, invitation_id=None):
        """Decline an organization invitation using the invitation ID."""
        try:
            # Get the invitation directly using its ID
            member = get_object_or_404(OrganizationMember, id=invitation_id)
            
            # Verify the invitation belongs to the current user (either by user or email)
            user_email = request.user.email
            if (member.user and member.user != request.user) and (member.invitation_email and member.invitation_email != user_email):
                return Response(
                    {"error": "This invitation does not belong to you"},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            # Delete the member
            member.delete()
            
            return Response(status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
