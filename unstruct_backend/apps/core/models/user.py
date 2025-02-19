from django.contrib.auth.models import AbstractUser
from django.db import models, transaction
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.common.models import NBaseModel


class User(AbstractUser, NBaseModel):
    personal_organization = models.OneToOneField(
        'core.Organization',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='personal_user'
    )


@receiver(post_save, sender=User)
def create_personal_organization(sender, instance, created, **kwargs):
    """Create personal organization for new users"""
    if created and not instance.personal_organization:
        from apps.core.models.organization import Organization, OrganizationMember
        
        with transaction.atomic():
            # Create personal organization with free plan
            org = Organization.objects.create(
                name=f"personal",
                description="Personal Organization",
                owner=instance,
                current_subscription_plan='free'  # Set default plan to free
            )
            
            # Set personal organization
            instance.personal_organization = org
            instance.save(update_fields=['personal_organization'])
            
            # Create admin membership
            OrganizationMember.objects.create(
                organization=org,
                user=instance,
                role='admin',
                invitation_accepted=True
            )
