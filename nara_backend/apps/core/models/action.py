from django.db import models
from django.utils.translation import gettext_lazy as _

from .base import NBaseModel
from .task import Task


class ACTION_TYPE(models.TextChoices):
    EXTRACTION = "EXTRACT", _("Extraction")
    GENERATION = "GENERATE", _("Generation")


class AGENT_TYPE(models.TextChoices):
    GPT_4O = "GPT_4O", _("GPT_4o")
    ANTHROPIC = "ANTHROPIC", _("Anthropic")


class Action(NBaseModel):
    name = models.CharField(max_length=200)
    task = models.ForeignKey(Task, blank=False, on_delete=models.DO_NOTHING)
    action_type = models.CharField(
        max_length=200, choices=ACTION_TYPE, default=ACTION_TYPE.EXTRACTION
    )
    agent_type = models.CharField(
        max_length=200, choices=AGENT_TYPE, default=AGENT_TYPE.GPT_4O
    )
    agent_metadata = models.JSONField(blank=True, default=dict)

    def __str__(self):
        return self.name
