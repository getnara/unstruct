from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.models import NBaseWithOwnerModel

from .action import Action
from .asset import Asset
from .project import Project


class TASK_RUNNING_STATUS(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    RUNNING = "RUNNING", _("Running")
    COMPLETED = "FINISHED", _("Finished")
    FAILED = "FAILED", _("Failed")


class Task(NBaseWithOwnerModel):
    name = models.CharField(max_length=200)
    project = models.ForeignKey(
        Project,
        blank=False,
        on_delete=models.CASCADE,
    )
    system_prompt = models.TextField()
    assets = models.ManyToManyField(
        Asset,
        related_name="assets",
        default=list,
    )
    actions = models.ManyToManyField(
        Action,
        related_name="actions",
        default=list,
    )
    status = models.CharField(max_length=200, choices=TASK_RUNNING_STATUS, default=TASK_RUNNING_STATUS.PENDING)

    result_file_url = models.URLField()

    def __str__(self):
        return self.name
