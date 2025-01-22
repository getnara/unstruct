from django.db import migrations
from django.utils import timezone

def update_lease_template(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TemplateAction = apps.get_model('core', 'TemplateAction')
    
    # First, delete existing lease template and its actions
    lease_template = TransformationTemplate.objects.filter(template_type='lease').first()
    if lease_template:
        lease_template.delete()
    
    # Create new lease template
    lease_template = TransformationTemplate.objects.create(
        name='Lease Abstraction',
        description='Extract key information from lease agreements including tenant details, rent terms, and property information',
        template_type='lease',
        image_url='https://storage.googleapis.com/nara-templates/lease-abstraction.jpg',
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    
    # Create individual actions for each field
    actions_data = [
        {
            'name': 'Tenant Name',
            'description': 'Extract the full legal name of the tenant',
            'fields': ['tenant_name']
        },
        {
            'name': 'Yearly Rent Increase',
            'description': 'Extract the annual percentage increase in rent',
            'fields': ['yearly_rent_increase_percentage']
        },
        {
            'name': 'Use Restrictions',
            'description': 'Extract any specific restrictions on how the leased premises can be used',
            'fields': ['specific_use_restrictions_for_the_leased_premises']
        },
        {
            'name': 'Landlord Name',
            'description': 'Extract the full legal name of the landlord',
            'fields': ['landlord_name']
        },
        {
            'name': 'Security Deposit',
            'description': 'Extract the amount of security deposit required',
            'fields': ['security_deposit_amount']
        },
        {
            'name': 'Monthly Base Rent',
            'description': 'Extract the monthly base rent amount',
            'fields': ['monthly_base_rent']
        },
        {
            'name': 'Property Address',
            'description': 'Extract the complete address of the leased premises',
            'fields': ['address_of_the_leased_premises']
        },
        {
            'name': 'Lease Start Date',
            'description': 'Extract the commencement date of the lease',
            'fields': ['lease_commencement_date']
        },
        {
            'name': 'Lease End Date',
            'description': 'Extract the termination date of the lease agreement',
            'fields': ['termination_date_of_the_lease_agreement']
        },
        {
            'name': 'Early Termination',
            'description': 'Extract conditions and terms for early lease termination',
            'fields': ['conditions_for_early_lease_termination']
        }
    ]
    
    for action_data in actions_data:
        TemplateAction.objects.create(
            template=lease_template,
            name=action_data['name'],
            description=action_data['description'],
            action_type='extraction',
            configuration={'fields': action_data['fields']},
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

def reverse_migration(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TransformationTemplate.objects.filter(template_type='lease').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0027_update_demographics_description'),
    ]

    operations = [
        migrations.RunPython(update_lease_template, reverse_migration),
    ] 