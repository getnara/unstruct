# Generated by Django 5.1.1 on 2025-01-23 14:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0031_add_additional_templates'),
    ]

    operations = [
        migrations.AddField(
            model_name='transformationtemplate',
            name='is_global',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='transformationtemplate',
            name='organization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='transformation_templates', to='core.organization'),
        ),
    ]
