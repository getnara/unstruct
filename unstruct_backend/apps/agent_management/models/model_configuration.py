from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import NBaseModel


class MODEL_TYPE(models.TextChoices):
    GPT_4O = "GPT_4O", _("GPT_4o")
    ANTHROPIC = "ANTHROPIC", _("Anthropic")


class ModelConfiguration(NBaseModel):
    name = models.CharField(max_length=200, unique=True)
    key = models.CharField(max_length=200, unique=True)
    model_config_data = models.JSONField(blank=True, default=dict)

    def __str__(self):
        return self.name
