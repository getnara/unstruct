# Generated by Django 5.1.1 on 2024-12-06 11:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_organization_current_subscription_plan_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='organization',
            name='stripe_customer_id',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='stripe_subscription_id',
        ),
    ]
