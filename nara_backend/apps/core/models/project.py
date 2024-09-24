from django.conf import settings
from django.db import models

from apps.common.models import NBaseWithOwnerModel


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

    def __str__(self) -> str:
        return str(self.name)
