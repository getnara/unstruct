# Generated by Django 5.1.1 on 2024-12-13 22:18

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_asset_mime_type_asset_size_alter_asset_upload_source'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='asset',
            options={'base_manager_name': 'objects', 'default_manager_name': 'objects'},
        ),
        migrations.RenameField(
            model_name='asset',
            old_name='dropbox_access_token',
            new_name='source_credentials',
        ),
        migrations.RenameField(
            model_name='asset',
            old_name='s3_key',
            new_name='source_file_id',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='dropbox_path',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='gdrive_credentials',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='gdrive_file_id',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='s3_bucket',
        ),
        migrations.RemoveField(
            model_name='asset',
            name='s3_credentials',
        ),
    ]
