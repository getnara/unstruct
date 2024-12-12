from rest_framework import serializers

from apps.common.models import NBaseModel


class NBaseSerializer(serializers.ModelSerializer):
    created_by_email = serializers.EmailField(source='created_by.email', read_only=True)
    updated_by_email = serializers.EmailField(source='updated_by.email', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    organization_id = serializers.CharField(source='organization.id', read_only=True)

    class Meta:
        model = NBaseModel
        fields = ['id', 'created_at', 'updated_at', 'created_by', 'updated_by', 
                 'created_by_email', 'updated_by_email', 'organization', 
                 'organization_id', 'organization_name']
        read_only_fields = ['created_by', 'updated_by', 'organization']
