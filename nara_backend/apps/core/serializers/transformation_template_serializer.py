from rest_framework import serializers
from apps.core.models.transformation_template import TransformationTemplate, TemplateAction

class TemplateActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateAction
        fields = ['id', 'name', 'description', 'action_type', 'configuration']

class TransformationTemplateSerializer(serializers.ModelSerializer):
    actions = TemplateActionSerializer(many=True, required=False)
    organization_id = serializers.UUIDField(source='organization.id', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    
    class Meta:
        model = TransformationTemplate
        fields = [
            'id', 'name', 'description', 'template_type', 'image_url',
            'organization_id', 'organization_name', 'is_global', 'actions'
        ]
        read_only_fields = ['organization_id', 'organization_name']

    def create(self, validated_data):
        actions_data = validated_data.pop('actions', [])
        template = TransformationTemplate.objects.create(**validated_data)
        
        for action_data in actions_data:
            TemplateAction.objects.create(template=template, **action_data)
        
        return template 