from django.db import models
from apps.common.models import NBaseModel

class TransformationTemplate(NBaseModel):
    """Model to store document transformation templates"""
    name = models.CharField(max_length=255)
    description = models.TextField()
    template_type = models.CharField(max_length=100)
    image_url = models.URLField(null=True, blank=True)
    
    class Meta:
        db_table = 'transformation_template'
        ordering = ['name']

    def __str__(self):
        return self.name

class TemplateAction(NBaseModel):
    """Model to store actions associated with templates"""
    template = models.ForeignKey(TransformationTemplate, on_delete=models.CASCADE, related_name='actions')
    name = models.CharField(max_length=255)
    description = models.TextField()
    action_type = models.CharField(max_length=100)
    configuration = models.JSONField(default=dict)
    
    class Meta:
        db_table = 'template_action'
        ordering = ['name']

    def __str__(self):
        return f"{self.template.name} - {self.name}" 