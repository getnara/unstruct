# Generated by Django 5.1.1 on 2024-11-18 15:29

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_asset_gdrive_file_id_alter_asset_file_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='asset',
            name='gdrive_credentials',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='asset',
            name='file_type',
            field=models.CharField(choices=[('PDF', 'Pdf'), ('MP4', 'Mp4'), ('DOC', 'Doc'), ('TXT', 'Text'), ('JPEG', 'Jpeg'), ('JPG', 'Jpg'), ('PNG', 'Png'), ('MP3', 'Mp3'), ('OTHER', 'Other')], default='OTHER', max_length=20),
        ),
        migrations.AlterField(
            model_name='asset',
            name='project',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assets', to='core.project'),
        ),
        migrations.AlterField(
            model_name='asset',
            name='upload_source',
            field=models.CharField(choices=[('UPLOAD', 'Upload'), ('GOOGLE_DRIVE', 'Google Drive'), ('DROPBOX', 'DropBox'), ('AWS_S3', 'Amazon S3')], default='UPLOAD', max_length=20),
        ),
        migrations.AlterField(
            model_name='asset',
            name='url',
            field=models.URLField(max_length=500),
        ),
    ]
