from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import NBaseWithOwnerModel

class ACTION_TYPE(models.TextChoices):
    EXTRACTION = "EXTRACT", _("Extraction")
    GENERATION = "GENERATE", _("Generation")

class OUTPUT_COLUMN_TYPE(models.TextChoices):
    TEXT = "TEXT", _("Text")
    NUMBER = "NUMBER", _("Number")
    DATE = "DATE", _("Date")

class Action(NBaseWithOwnerModel):
    output_column_name = models.CharField(max_length=200)
    output_column_type = models.CharField(max_length=50, choices=OUTPUT_COLUMN_TYPE, default=OUTPUT_COLUMN_TYPE.TEXT)
    action_type = models.CharField(max_length=200, choices=ACTION_TYPE, default=ACTION_TYPE.EXTRACTION)
    description = models.TextField()

    def __str__(self):
        return self.output_column_name
