# Generated by Django 5.1.1 on 2024-12-08 07:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_organization_media_gb_processed_this_month_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='subscription_current_period_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='subscription_current_period_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
