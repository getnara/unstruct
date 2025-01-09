from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0007_task_completed_at_task_description_task_failed_files_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(
                choices=[
                    ('PENDING', 'Pending'),
                    ('RUNNING', 'Running'),
                    ('FINISHED', 'Finished'),
                    ('FAILED', 'Failed')
                ],
                default='PENDING',
                max_length=200
            ),
        ),
    ] 