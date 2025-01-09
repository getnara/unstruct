from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0021_merge_20240213_fix_task_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='process_results',
            field=models.TextField(blank=True, default='[]'),
        ),
    ] 