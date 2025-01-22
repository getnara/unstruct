from django.db import migrations
from django.utils import timezone

def update_medical_template(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TemplateAction = apps.get_model('core', 'TemplateAction')
    
    # First, delete existing medical template and its actions
    medical_template = TransformationTemplate.objects.filter(template_type='medical').first()
    if medical_template:
        medical_template.delete()
    
    # Create new medical template with individual actions
    medical_template = TransformationTemplate.objects.create(
        name='Medical Documents',
        description='Extract key study information, participant data, and research findings from medical research documents',
        template_type='medical',
        image_url='https://storage.googleapis.com/nara-templates/medical-documents.jpg',
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    
    # Create individual actions
    actions_data = [
        {
            'name': 'Authors',
            'description': 'Extract names of the authors involved in the study',
            'fields': ['names_of_the_authors_involved_in_the_study']
        },
        {
            'name': 'Primary Objective',
            'description': 'Identify the primary objective of the study',
            'fields': ['identify_the_primary_objective_of_the_study_']
        },
        {
            'name': 'Conflicts of Interest',
            'description': 'Extract conflicts of interest disclosed by authors',
            'fields': ['conflicts_of_interest_disclosed_by_authors']
        },
        {
            'name': 'Participant Count',
            'description': 'Extract the number of participants in the study',
            'fields': ['number_of_participants']
        },
        {
            'name': 'Primary Endpoints',
            'description': 'Extract the primary endpoints of the study',
            'fields': ['primary_endpoints_of_the_study']
        },
        {
            'name': 'Study Duration',
            'description': 'Extract the duration of the study',
            'fields': ['duration_of_the_study']
        },
        {
            'name': 'Study Design',
            'description': 'Extract study design and methodology',
            'fields': ['study_design_and_methodology']
        },
        {
            'name': 'Treatment Safety',
            'description': 'Extract information about the safety of the treatment',
            'fields': ['safety_of_the_treatment']
        },
        {
            'name': 'Adverse Events',
            'description': 'Extract adverse events reported during the study',
            'fields': ['adverse_events_reported_during_the_study']
        },
        {
            'name': 'Demographics',
            'description': 'Output a string detailing age ranges, gender distribution, ethnicity breakdown, and other key demographic characteristics of the study participants',
            'fields': ['demographic_characteristics_of_the_participants']
        }
    ]
    
    for action_data in actions_data:
        TemplateAction.objects.create(
            template=medical_template,
            name=action_data['name'],
            description=action_data['description'],
            action_type='extraction',
            configuration={'fields': action_data['fields']},
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

def reverse_migration(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TransformationTemplate.objects.filter(template_type='medical').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0025_merge_20250116_1617'),
    ]

    operations = [
        migrations.RunPython(update_medical_template, reverse_migration),
    ] 