from django.db import migrations
from django.utils import timezone

def update_utility_template(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TemplateAction = apps.get_model('core', 'TemplateAction')
    
    # First, delete existing utility template and its actions
    utility_template = TransformationTemplate.objects.filter(template_type='utility').first()
    if utility_template:
        utility_template.delete()
    
    # Create new utility template
    utility_template = TransformationTemplate.objects.create(
        name='Utility Bills',
        description='Extract key information from utility bills including customer details, charges, and payment information',
        template_type='utility',
        image_url='https://storage.googleapis.com/nara-templates/utility-bills.jpg',
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    
    # Create individual actions for each field
    actions_data = [
        {
            'name': 'Payment Methods',
            'description': 'Extract available payment methods for the bill',
            'fields': ['payment_methods']
        },
        {
            'name': 'Customer Name',
            'description': 'Extract the full name of the customer',
            'fields': ['customer_s_name']
        },
        {
            'name': 'Current Charges',
            'description': 'Extract the current billing period charges',
            'fields': ['current_charges']
        },
        {
            'name': 'Payment Due Date',
            'description': 'Extract the due date for payment',
            'fields': ['due_date_for_payment']
        },
        {
            'name': 'Billing Date',
            'description': 'Extract the date when the bill was issued',
            'fields': ['billing_date']
        },
        {
            'name': 'Account Number',
            'description': 'Extract the customer account number',
            'fields': ['account_number']
        },
        {
            'name': 'Total Amount Due',
            'description': 'Extract the total amount due including any previous balance',
            'fields': ['total_amount_due']
        },
        {
            'name': 'Utility Provider',
            'description': 'Extract the name of the utility service provider',
            'fields': ['utility_provider_s_name']
        },
        {
            'name': 'Previous Balance',
            'description': 'Extract the previous balance amount carried forward',
            'fields': ['previous_balance_amount']
        },
        {
            'name': 'Service Address',
            'description': 'Extract the address where utility service is provided',
            'fields': ['service_location_address']
        }
    ]
    
    for action_data in actions_data:
        TemplateAction.objects.create(
            template=utility_template,
            name=action_data['name'],
            description=action_data['description'],
            action_type='extraction',
            configuration={'fields': action_data['fields']},
            created_at=timezone.now(),
            updated_at=timezone.now()
        )

def reverse_migration(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TransformationTemplate.objects.filter(template_type='utility').delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0028_update_lease_template'),
    ]

    operations = [
        migrations.RunPython(update_utility_template, reverse_migration),
    ] 