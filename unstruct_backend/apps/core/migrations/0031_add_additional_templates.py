from django.db import migrations
from django.utils import timezone

def add_additional_templates(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TemplateAction = apps.get_model('core', 'TemplateAction')
    
    templates_data = [
        {
            'name': 'RFP Documents',
            'description': 'Extract project scope, deadlines, success criteria and more from RFP documents',
            'template_type': 'rfp',
            'image_url': 'https://storage.googleapis.com/nara-templates/rfp-documents.jpg',
            'actions': [
                {
                    'name': 'Contract Duration',
                    'description': 'Extract the duration or term of the contract',
                    'fields': ['duration_of_contract']
                },
                {
                    'name': 'Contractor Responsibilities',
                    'description': 'Extract detailed responsibilities and obligations of the contractor',
                    'fields': ['extract_the_responsibilities_of_the_contractor_']
                },
                {
                    'name': 'RFP Title',
                    'description': 'Extract the title or name of the RFP',
                    'fields': ['rfp_title']
                },
                {
                    'name': 'Contact Person',
                    'description': 'Extract contact information for RFP inquiries',
                    'fields': ['contact_person_for_the_rfp']
                },
                {
                    'name': 'Evaluation Criteria',
                    'description': 'Extract criteria for evaluating submitted proposals',
                    'fields': ['evaluation_criteria_for_proposals']
                },
                {
                    'name': 'Insurance Requirements',
                    'description': 'Extract required insurance coverage and limits',
                    'fields': ['insurance_requirements']
                },
                {
                    'name': 'Submission Location',
                    'description': 'Extract where and how proposals should be submitted',
                    'fields': ['location_where_proposals_should_be_submitted']
                },
                {
                    'name': 'Submission Deadline',
                    'description': 'Extract the deadline for proposal submissions',
                    'fields': ['submission_deadline_for_proposals']
                },
                {
                    'name': 'Governing Law',
                    'description': 'Extract applicable laws and jurisdiction',
                    'fields': ['governing_law']
                },
                {
                    'name': 'Budget Estimate',
                    'description': 'Extract estimated budget or cost requirements',
                    'fields': ['budget_cost_estimate']
                }
            ]
        },
        {
            'name': 'Job Resumes',
            'description': 'Extract candidate details, skills, work history, education, and key qualifications',
            'template_type': 'resume',
            'image_url': 'https://storage.googleapis.com/nara-templates/job-resumes.jpg',
            'actions': [
                {
                    'name': 'Job Title',
                    'description': 'Extract the current or desired job title',
                    'fields': ['job_title']
                },
                {
                    'name': 'City',
                    'description': 'Extract the city of residence or work location',
                    'fields': ['city']
                },
                {
                    'name': 'Professional Overview',
                    'description': 'Extract professional summary and career objectives',
                    'fields': ['professional_overview']
                },
                {
                    'name': 'Name',
                    'description': 'Extract the full name of the candidate',
                    'fields': ['name']
                },
                {
                    'name': 'Key Skills',
                    'description': 'Extract primary skills and competencies',
                    'fields': ['key_skills']
                },
                {
                    'name': 'Education',
                    'description': 'Extract educational background and qualifications',
                    'fields': ['education']
                }
            ]
        },
        {
            'name': 'Lab Reports',
            'description': 'Extract test types, results, reference ranges, and clinical interpretation details',
            'template_type': 'lab',
            'image_url': 'https://storage.googleapis.com/nara-templates/lab-reports.jpg',
            'actions': [
                {
                    'name': 'Clinical Implications',
                    'description': 'Extract clinical implications and significance of findings',
                    'fields': ['clinical_implications']
                },
                {
                    'name': 'Diagnosis Summary',
                    'description': 'Extract summary of diagnostic findings and conclusions',
                    'fields': ['diagnosis_summary']
                },
                {
                    'name': 'Specimen Type',
                    'description': 'Extract type and nature of specimen analyzed',
                    'fields': ['specimen_type']
                },
                {
                    'name': 'Pathological Stage',
                    'description': 'Extract pathological staging information if applicable',
                    'fields': ['pathological_stage']
                },
                {
                    'name': 'Follow-up Recommendations',
                    'description': 'Extract recommended follow-up actions and monitoring',
                    'fields': ['follow_up_recommendations']
                },
                {
                    'name': 'Abnormal Findings',
                    'description': 'Extract any abnormal or significant findings',
                    'fields': ['abnormal_findings']
                }
            ]
        },
        {
            'name': 'Master Supply Agreements',
            'description': 'Extract terms of delivery, payment conditions, and more from Master Supply Agreements',
            'template_type': 'msa',
            'image_url': 'https://storage.googleapis.com/nara-templates/master-supply-agreements.jpg',
            'actions': [
                {
                    'name': 'Payment Conditions',
                    'description': 'Extract payment terms, schedules, and financial obligations',
                    'fields': ['payment_conditions']
                },
                {
                    'name': 'Dispute Resolution',
                    'description': 'Extract terms and procedures for resolving disputes',
                    'fields': ['dispute_resolution_terms']
                },
                {
                    'name': 'Product Specifications',
                    'description': 'Extract detailed specifications of products or services',
                    'fields': ['product_specifications']
                },
                {
                    'name': 'Party Names',
                    'description': 'Extract names of supplier and buyer parties',
                    'fields': ['supplier_and_buyer_names']
                },
                {
                    'name': 'Delivery Terms',
                    'description': 'Extract terms and conditions for delivery',
                    'fields': ['delivery_terms']
                },
                {
                    'name': 'Contract Duration',
                    'description': 'Extract contract duration and termination conditions',
                    'fields': ['contract_duration_and_termination']
                }
            ]
        }
    ]
    
    for template_data in templates_data:
        # Delete existing template if it exists
        existing_template = TransformationTemplate.objects.filter(template_type=template_data['template_type']).first()
        if existing_template:
            existing_template.delete()
            
        # Create new template
        template = TransformationTemplate.objects.create(
            name=template_data['name'],
            description=template_data['description'],
            template_type=template_data['template_type'],
            image_url=template_data['image_url'],
            created_at=timezone.now(),
            updated_at=timezone.now()
        )
        
        # Create actions for the template
        for action_data in template_data['actions']:
            TemplateAction.objects.create(
                template=template,
                name=action_data['name'],
                description=action_data['description'],
                action_type='extraction',
                configuration={'fields': action_data['fields']},
                created_at=timezone.now(),
                updated_at=timezone.now()
            )

def reverse_migration(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    template_types = ['rfp', 'resume', 'lab', 'msa']
    TransformationTemplate.objects.filter(template_type__in=template_types).delete()

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0030_update_fda_template'),
    ]

    operations = [
        migrations.RunPython(add_additional_templates, reverse_migration),
    ] 