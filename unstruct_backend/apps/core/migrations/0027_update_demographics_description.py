from django.db import migrations
from django.utils import timezone

def update_demographics_description(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TemplateAction = apps.get_model('core', 'TemplateAction')
    
    medical_template = TransformationTemplate.objects.filter(template_type='medical').first()
    if medical_template:
        demographics_action = TemplateAction.objects.filter(
            template=medical_template,
            name='Demographics'
        ).first()
        if demographics_action:
            demographics_action.description = 'Output a string detailing age ranges, gender distribution, ethnicity breakdown, and other key demographic characteristics of the study participants'
            demographics_action.updated_at = timezone.now()
            demographics_action.save()

def reverse_migration(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TemplateAction = apps.get_model('core', 'TemplateAction')
    
    medical_template = TransformationTemplate.objects.filter(template_type='medical').first()
    if medical_template:
        demographics_action = TemplateAction.objects.filter(
            template=medical_template,
            name='Demographics'
        ).first()
        if demographics_action:
            demographics_action.description = 'Extract demographic characteristics of the participants'
            demographics_action.updated_at = timezone.now()
            demographics_action.save()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0026_update_medical_template'),
    ]

    operations = [
        migrations.RunPython(update_demographics_description, reverse_migration),
    ] 