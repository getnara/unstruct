from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import NBaseModel
from .project import Project


class ASSET_UPLOAD_SOURCE(models.TextChoices):
    UPLOAD = "UPLOAD", _("Upload")
    GDRIVE = "GOOGLE_DRIVE", _("Google Drive")
    DROPBOX = "DROPBOX", _("DropBox")
    AWS_S3 = "AWS_S3", _("Amazon S3")


class ASSET_FILE_TYPE(models.TextChoices):
    PDF = "PDF", _("Pdf")
    DOC = "DOC", _("Doc")
    TXT = "TXT", _("Text")
    OTHER = "OTHER", _("Other")


class Asset(NBaseModel):
    """Represents a asset in the system."""

    name = models.CharField(max_length=200)
    description = models.TextField()
    project = models.ForeignKey(
        Project,
        blank=False,
        on_delete=models.CASCADE,
    )
    url = models.URLField()
    upload_source = models.CharField(
        max_length=200,
        choices=ASSET_UPLOAD_SOURCE,
    )
    file_type = models.CharField(max_length=200, choices=ASSET_FILE_TYPE, default=ASSET_FILE_TYPE.OTHER)

    def __str__(self) -> str:
        return str(self.name)
