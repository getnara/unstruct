from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import NBaseWithOwnerModel
from .constants import ASSET_UPLOAD_SOURCE


class Project(NBaseWithOwnerModel):
    """Represents a project in the system."""

    name = models.CharField(max_length=200)
    description = models.TextField()
    collaborators = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="collaborators",
        default=list,
        blank=True,
    )
    data_source_type = models.CharField(
        max_length=200,
        choices=[
            ('UPLOAD', 'Upload'),
            ('GOOGLE_DRIVE', 'Google Drive'),
            ('DROPBOX', 'DropBox'),
            ('AWS_S3', 'Amazon S3')
        ],
        default='UPLOAD',
    )

    def __str__(self) -> str:
        return str(self.name)
