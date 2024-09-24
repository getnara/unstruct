from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import NBaseWithOwnerModel


class ACTION_TYPE(models.TextChoices):
    EXTRACTION = "EXTRACT", _("Extraction")
    GENERATION = "GENERATE", _("Generation")


class Action(NBaseWithOwnerModel):
    name = models.CharField(max_length=200)
    description = models.TextField()
    action_type = models.CharField(max_length=200, choices=ACTION_TYPE, default=ACTION_TYPE.EXTRACTION)

    def __str__(self):
        return self.name
