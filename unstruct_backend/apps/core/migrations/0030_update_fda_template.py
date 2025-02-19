from django.db import migrations
from django.utils import timezone

def update_fda_template(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TemplateAction = apps.get_model('core', 'TemplateAction')
    
    # First, delete existing FDA template and its actions
    fda_template = TransformationTemplate.objects.filter(template_type='fda').first()
    if fda_template:
        fda_template.delete()
    
    # Create new FDA template
    fda_template = TransformationTemplate.objects.create(
        name='FDA Approved Documents',
        description='Extract key information from FDA approved documents including safety measures, controls, and guidelines',
        template_type='fda',
        image_url='https://storage.googleapis.com/nara-templates/fda-documents.jpg',
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    
    # Create individual actions for each field
    actions_data = [
        {
            'name': 'Distribution Controls',
            'description': 'Extract information about distribution and dispensing control measures',
            'fields': ['distribution_and_dispensing_controls']
        },
        {
            'name': 'Provider Training',
            'description': 'Extract requirements and guidelines for healthcare provider training',
            'fields': ['healthcare_provider_training']
        },
        {
            'name': 'Adverse Events',
            'description': 'Extract procedures and requirements for adverse event reporting',
            'fields': ['adverse_event_reporting']
        },
        {
            'name': 'Usage Guidelines',
            'description': 'Extract guidelines and instructions for medication use',
            'fields': ['medication_use_guidelines']
        },
        {
            'name': 'Patient Monitoring',
            'description': 'Extract requirements for monitoring patients during treatment',
            'fields': ['patient_monitoring_requirements']
        },
        {
            'name': 'Risk Identification',
            'description': 'Extract information about identified risks and safety concerns',
            'fields': ['risk_identification']
        }
    ]
    
    for action_data in actions_data:
        TemplateAction.objects.create(
            template=fda_template,
            name=action_data['name'],
            description=action_data['description'],
            action_type='extraction',
            configuration={'fields': action_data['fields']},
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

def reverse_migration(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TransformationTemplate.objects.filter(template_type='fda').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0029_update_utility_template'),
    ]

    operations = [
        migrations.RunPython(update_fda_template, reverse_migration),
    ] 