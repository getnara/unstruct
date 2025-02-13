from django.db import migrations

def set_templates_global(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TransformationTemplate.objects.all().update(is_global=True)

def reverse_templates_global(apps, schema_editor):
    TransformationTemplate = apps.get_model('core', 'TransformationTemplate')
    TransformationTemplate.objects.all().update(is_global=False)

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0031_add_additional_templates'),  # Update this to your last migration
    ]

    operations = [
        migrations.RunPython(set_templates_global, reverse_templates_global),
    ] 