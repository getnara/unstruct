from django.db import migrations
from django.utils import timezone

def create_initial_templates(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TemplateAction = apps.get_model('core', 'TemplateAction')
    
    # Create templates
    templates_data = [
        {
            'name': 'Medical Documents',
            'description': 'Extract key study information, participant data, and research findings from medical research documents',
            'template_type': 'medical',
            'image_url': 'https://storage.googleapis.com/nara-templates/medical-documents.jpg',
            'actions': [
                {
                    'name': 'Authors',
                    'description': 'Extract names of the authors involved in the study',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['names_of_the_authors_involved_in_the_study']
                    }
                },
                {
                    'name': 'Primary Objective',
                    'description': 'Identify the primary objective of the study',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['identify_the_primary_objective_of_the_study_']
                    }
                },
                {
                    'name': 'Conflicts of Interest',
                    'description': 'Extract conflicts of interest disclosed by authors',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['conflicts_of_interest_disclosed_by_authors']
                    }
                },
                {
                    'name': 'Participant Count',
                    'description': 'Extract the number of participants in the study',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['number_of_participants']
                    }
                },
                {
                    'name': 'Primary Endpoints',
                    'description': 'Extract the primary endpoints of the study',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['primary_endpoints_of_the_study']
                    }
                },
                {
                    'name': 'Study Duration',
                    'description': 'Extract the duration of the study',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['duration_of_the_study']
                    }
                },
                {
                    'name': 'Study Design',
                    'description': 'Extract study design and methodology',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['study_design_and_methodology']
                    }
                },
                {
                    'name': 'Treatment Safety',
                    'description': 'Extract information about the safety of the treatment',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['safety_of_the_treatment']
                    }
                },
                {
                    'name': 'Adverse Events',
                    'description': 'Extract adverse events reported during the study',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['adverse_events_reported_during_the_study']
                    }
                },
                {
                    'name': 'Demographics',
                    'description': 'Extract demographic characteristics of the participants',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['demographic_characteristics_of_the_participants']
                    }
                }
            ]
        },
        {
            'name': 'Lease Abstraction',
            'description': 'Extract lease terms, dates, financial obligations, and more from complex lease agreements',
            'template_type': 'lease',
            'image_url': 'https://storage.googleapis.com/nara-templates/lease-abstraction.jpg',
            'actions': [
                {
                    'name': 'Extract Lease Terms',
                    'description': 'Extract key lease terms and dates',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['start_date', 'end_date', 'renewal_terms', 'notice_period']
                    }
                },
                {
                    'name': 'Extract Financial Terms',
                    'description': 'Extract rent and other financial obligations',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['base_rent', 'security_deposit', 'maintenance_fees', 'utilities']
                    }
                }
            ]
        },
        {
            'name': 'Utility Bills',
            'description': 'Extract usage details, billing history, payment terms, and more from utility bills',
            'template_type': 'utility',
            'image_url': 'https://storage.googleapis.com/nara-templates/utility-bills.jpg',
            'actions': [
                {
                    'name': 'Extract Usage Details',
                    'description': 'Extract utility usage information',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['meter_reading', 'consumption', 'billing_period', 'rate_plan']
                    }
                },
                {
                    'name': 'Extract Payment Information',
                    'description': 'Extract billing and payment details',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['amount_due', 'due_date', 'payment_methods', 'late_fees']
                    }
                }
            ]
        },
        {
            'name': 'FDA Compliance Documents',
            'description': 'Extract risk assessments, medication use guidelines, and adverse event reports',
            'template_type': 'fda',
            'image_url': 'https://storage.googleapis.com/nara-templates/fda-compliance.jpg',
            'actions': [
                {
                    'name': 'Extract Risk Assessments',
                    'description': 'Extract risk assessment information',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['risk_factors', 'severity', 'mitigation_measures', 'recommendations']
                    }
                },
                {
                    'name': 'Extract Adverse Events',
                    'description': 'Extract adverse event report details',
                    'action_type': 'extraction',
                    'configuration': {
                        'fields': ['event_date', 'description', 'outcome', 'follow_up_actions']
                    }
                }
            ]
        }
    ]
    
    for template_data in templates_data:
        actions = template_data.pop('actions')
        template = TransformationTemplate.objects.create(
            **template_data,
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        for action_data in actions:
            TemplateAction.objects.create(
                template=template,
                **action_data,
                created_at=timezone.now(),
                updated_at=timezone.now()
            )

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0023_transformation_templates_models'),
    ]

    operations = [
        migrations.RunPython(create_initial_templates)
    ] 