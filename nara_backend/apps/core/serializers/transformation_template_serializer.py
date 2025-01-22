from rest_framework import serializers
from apps.core.models.transformation_template import TransformationTemplate, TemplateAction

class TemplateActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateAction
        fields = ['id', 'name', 'description', 'action_type', 'configuration']

class TransformationTemplateSerializer(serializers.ModelSerializer):
    actions = TemplateActionSerializer(many=True, read_only=True)
    
    class Meta:
        model = TransformationTemplate
        fields = ['id', 'name', 'description', 'template_type', 'image_url', 'actions'] 