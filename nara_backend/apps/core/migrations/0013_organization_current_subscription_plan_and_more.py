# Generated by Django 5.1.1 on 2024-12-06 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_remove_organization_current_subscription_plan_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='organization',
            name='current_subscription_plan',
            field=models.CharField(choices=[('free', 'Free'), ('pro', 'Pro')], default='free', max_length=50),
        ),
        migrations.AddField(
            model_name='organization',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='organization',
            name='stripe_subscription_id',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
