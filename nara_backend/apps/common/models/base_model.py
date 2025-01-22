import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone


class NBaseModelManager(models.Manager):
    def get_queryset(self):
        return super(NBaseModelManager, self).get_queryset().filter(is_deleted=False)


class NBaseModel(models.Model):
    """Base model with common fields and soft delete functionality"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_created"
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_updated"
    )
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        null=True,
        related_name="%(class)s_items"
    )

    objects = NBaseModelManager()
    all_objects = models.Manager()

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
    """Base model with owner field in addition to base fields"""
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="%(class)s_owner"
    )

    class Meta:
        abstract = True
