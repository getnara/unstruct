from django.conf import settings
from django.db import models

from .base import NBaseModel


class Project(NBaseModel):
    """Represents a project in the system."""

    name = models.CharField(max_length=200)
    description = models.TextField()
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        blank=False,
        on_delete=models.CASCADE,
    )

    def __str__(self) -> str:
        return str(self.name)
