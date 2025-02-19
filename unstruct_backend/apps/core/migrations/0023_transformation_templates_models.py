from django.db import migrations, models
import uuid


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0022_alter_task_process_results'),
    ]

    operations = [
        migrations.CreateModel(
            name='TransformationTemplate',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('template_type', models.CharField(max_length=100)),
                ('image_url', models.URLField(blank=True, null=True)),
                ('created_by', models.ForeignKey(null=True, on_delete=models.SET_NULL, related_name='%(class)s_created', to='core.user')),
                ('organization', models.ForeignKey(null=True, on_delete=models.CASCADE, related_name='%(class)s_items', to='core.organization')),
                ('updated_by', models.ForeignKey(null=True, on_delete=models.SET_NULL, related_name='%(class)s_updated', to='core.user')),
            ],
            options={
                'db_table': 'transformation_template',
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='TemplateAction',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('is_deleted', models.BooleanField(default=False)),
                ('deleted_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('action_type', models.CharField(max_length=100)),
                ('configuration', models.JSONField(default=dict)),
                ('created_by', models.ForeignKey(null=True, on_delete=models.SET_NULL, related_name='%(class)s_created', to='core.user')),
                ('organization', models.ForeignKey(null=True, on_delete=models.CASCADE, related_name='%(class)s_items', to='core.organization')),
                ('template', models.ForeignKey(on_delete=models.CASCADE, related_name='actions', to='core.transformationtemplate')),
                ('updated_by', models.ForeignKey(null=True, on_delete=models.SET_NULL, related_name='%(class)s_updated', to='core.user')),
            ],
            options={
                'db_table': 'template_action',
                'ordering': ['name'],
                'abstract': False,
            },
        ),
    ] 