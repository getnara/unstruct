import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class NBaseModelManager(models.Manager):
    def get_queryset(self):
        return super(NBaseModelManager, self).get_queryset().filter(is_deleted=False)


class NBaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created_by",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated_by",
    )

    class Meta:
        abstract = True

    def delete(self, hard=False, user=None, **kwargs):
        if user:
            self.updated_by = user
        if hard:
            super(NBaseModel, self).delete()
        else:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save()

    def restore(self, user=None):
        self.is_deleted = False
        self.deleted_at = None
        if user:
            self.updated_by = user
        self.save()


class NBaseWithOwnerModel(NBaseModel):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_owner",
    )

    class Meta:
        abstract = True
