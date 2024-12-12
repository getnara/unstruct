from rest_framework import serializers
from apps.core.models.organization import Organization, OrganizationMember


class OrganizationSerializer(serializers.ModelSerializer):
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)

    class Meta:
        model = Organization
        fields = ['id', 'name', 'description', 'owner', 'owner_email', 'owner_name', 'created_at', 'updated_at']
        read_only_fields = ['owner']


class OrganizationMemberSerializer(serializers.ModelSerializer):
    user_email = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = OrganizationMember
        fields = ['id', 'user', 'user_email', 'user_name', 'role', 'invitation_accepted', 'created_at']
        read_only_fields = ['invitation_accepted']

    def get_user_email(self, obj):
        # Return invitation_email for invited users, user.email for accepted users
        if obj.user:
            return obj.user.email
        return obj.invitation_email


class OrganizationInviteSerializer(serializers.Serializer):
    email = serializers.EmailField()
    role = serializers.ChoiceField(choices=OrganizationMember.ROLE_CHOICES, default='member')
