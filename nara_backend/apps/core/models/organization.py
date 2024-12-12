from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime

from apps.common.models import NBaseModel
from apps.core.services.stripe_service import StripeService


class Organization(NBaseModel):
    @classmethod
    def get_plan_limits(cls, plan_type):
        """Get plan limits from settings"""
        return settings.SUBSCRIPTION_PLANS.get(plan_type, settings.SUBSCRIPTION_PLANS['free'])

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_organizations'
    )
    current_subscription_plan = models.CharField(
        max_length=50,
        choices=settings.SUBSCRIPTION_PLAN_CHOICES,
        default='free'
    )
    
    # Usage tracking fields
    pdfs_processed_this_month = models.IntegerField(default=0)
    video_gb_processed_this_month = models.FloatField(default=0.0)
    audio_gb_processed_this_month = models.FloatField(default=0.0)
    usage_reset_date = models.DateTimeField(default=timezone.now)
    subscription_current_period_start = models.DateTimeField(null=True, blank=True)
    subscription_current_period_end = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.name
        
    def has_member(self, user):
        # Owner always has access
        if self.owner == user:
            return True
            
        # Check if user is a member with accepted invitation
        return self.members.filter(
            user=user,
            invitation_accepted=True
        ).exists()

    def reset_usage_if_needed(self):
        """Reset usage counters if we're in a new billing cycle"""
        now = timezone.now()
        stripe_service = StripeService()
        
        # Get current subscription period
        subscription_info = stripe_service.get_subscription_info_by_email(self.owner.email)
        
        if subscription_info:
            current_period_start = subscription_info['current_period_start']
            current_period_end = subscription_info['current_period_end']
            
            # If we have new period dates and they're different from stored ones
            if (current_period_start != self.subscription_current_period_start or 
                current_period_end != self.subscription_current_period_end):
                # Reset usage and update period dates
                self.pdfs_processed_this_month = 0
                self.video_gb_processed_this_month = 0.0
                self.audio_gb_processed_this_month = 0.0
                self.usage_reset_date = now
                self.subscription_current_period_start = current_period_start
                self.subscription_current_period_end = current_period_end
                self.save(update_fields=[
                    'pdfs_processed_this_month', 
                    'video_gb_processed_this_month',
                    'audio_gb_processed_this_month',
                    'usage_reset_date',
                    'subscription_current_period_start',
                    'subscription_current_period_end'
                ])
        else:
            # For free plans or when no subscription info is available,
            # fall back to calendar month reset
            if now.month != self.usage_reset_date.month or now.year != self.usage_reset_date.year:
                self.pdfs_processed_this_month = 0
                self.video_gb_processed_this_month = 0.0
                self.audio_gb_processed_this_month = 0.0
                self.usage_reset_date = now
                self.subscription_current_period_start = None
                self.subscription_current_period_end = None
                self.save(update_fields=[
                    'pdfs_processed_this_month', 
                    'video_gb_processed_this_month',
                    'audio_gb_processed_this_month',
                    'usage_reset_date',
                    'subscription_current_period_start',
                    'subscription_current_period_end'
                ])

    def can_process_pdf(self):
        """Check if organization can process more PDFs based on subscription plan"""
        self.reset_usage_if_needed()
        
        stripe_service = StripeService()
        subscription_status = stripe_service.get_subscription_status_by_email(self.owner.email)
        subscription_type = stripe_service.get_subscription_type_by_email(self.owner.email)
        
        # Use appropriate plan based on subscription
        if subscription_status == 'active':
            plan = subscription_type if subscription_type in settings.SUBSCRIPTION_PLANS else 'free'
        else:
            plan = 'free'
            
        plan_limits = self.get_plan_limits(plan)
        plan_name = settings.SUBSCRIPTION_PLAN_NAMES.get(plan, 'Free')
        
        if self.pdfs_processed_this_month >= plan_limits['max_pdfs_per_month']:
            raise ValidationError(
                f"Organization has reached the maximum PDF processing limit of {plan_limits['max_pdfs_per_month']} "
                f"for the {plan_name} plan this month"
            )
        return True

    def can_process_video(self, size_in_gb):
        """Check if organization can process more video based on subscription plan"""
        self.reset_usage_if_needed()
        
        stripe_service = StripeService()
        subscription_status = stripe_service.get_subscription_status_by_email(self.owner.email)
        subscription_type = stripe_service.get_subscription_type_by_email(self.owner.email)
        
        # Use appropriate plan based on subscription
        if subscription_status == 'active':
            plan = subscription_type if subscription_type in settings.SUBSCRIPTION_PLANS else 'free'
        else:
            plan = 'free'
            
        plan_limits = self.get_plan_limits(plan)
        plan_name = settings.SUBSCRIPTION_PLAN_NAMES.get(plan, 'Free')
            
        if self.video_gb_processed_this_month + size_in_gb > plan_limits['max_video_gb_per_month']:
            raise ValidationError(
                f"Processing this video would exceed the {plan_limits['max_video_gb_per_month']}GB "
                f"monthly limit for the {plan_name} plan. "
                f"Current usage: {self.video_gb_processed_this_month:.2f}GB"
            )
        return True

    def can_process_audio(self, size_in_gb):
        """Check if organization can process more audio based on subscription plan"""
        self.reset_usage_if_needed()
        
        stripe_service = StripeService()
        subscription_status = stripe_service.get_subscription_status_by_email(self.owner.email)
        subscription_type = stripe_service.get_subscription_type_by_email(self.owner.email)
        
        # Use appropriate plan based on subscription
        if subscription_status == 'active':
            plan = subscription_type if subscription_type in settings.SUBSCRIPTION_PLANS else 'free'
        else:
            plan = 'free'
            
        plan_limits = self.get_plan_limits(plan)
        plan_name = settings.SUBSCRIPTION_PLAN_NAMES.get(plan, 'Free')
            
        if self.audio_gb_processed_this_month + size_in_gb > plan_limits['max_audio_gb_per_month']:
            raise ValidationError(
                f"Processing this audio would exceed the {plan_limits['max_audio_gb_per_month']}GB "
                f"monthly limit for the {plan_name} plan. "
                f"Current usage: {self.audio_gb_processed_this_month:.2f}GB"
            )
        return True

    def increment_pdf_count(self):
        """Increment the PDF processing count"""
        self.reset_usage_if_needed()
        self.pdfs_processed_this_month += 1
        self.save(update_fields=['pdfs_processed_this_month'])

    def add_video_usage(self, size_in_gb):
        """Add to the video processing usage"""
        self.reset_usage_if_needed()
        self.video_gb_processed_this_month += size_in_gb
        self.save(update_fields=['video_gb_processed_this_month'])

    def add_audio_usage(self, size_in_gb):
        """Add to the audio processing usage"""
        self.reset_usage_if_needed()
        self.audio_gb_processed_this_month += size_in_gb
        self.save(update_fields=['audio_gb_processed_this_month'])

    def can_add_member(self):
        """Check if organization can add more members based on subscription plan"""
        # Check Stripe subscription status
        stripe_service = StripeService()
        subscription_status = stripe_service.get_subscription_status_by_email(self.owner.email)
        subscription_type = stripe_service.get_subscription_type_by_email(self.owner.email)
        
        # Use appropriate plan based on subscription
        if subscription_status == 'active':
            plan = subscription_type if subscription_type in settings.SUBSCRIPTION_PLANS else 'free'
        else:
            plan = 'free'
            
        plan_limits = self.get_plan_limits(plan)
        plan_name = settings.SUBSCRIPTION_PLAN_NAMES.get(plan, 'Free')
        
        # Count both accepted members and pending invites
        total_member_count = self.members.count()  # This includes both accepted and pending
        
        if total_member_count >= plan_limits['max_members']:
            raise ValidationError(
                f"Organization has reached the maximum member limit of {plan_limits['max_members']} "
                f"for the {plan_name} plan (including pending invites)"
            )
        return True

    @classmethod
    def can_create_organization(cls, user):
        """Check if user can create more organizations based on subscription plan"""
        # Check Stripe subscription status
        stripe_service = StripeService()
        subscription_status = stripe_service.get_subscription_status_by_email(user.email)
        subscription_type = stripe_service.get_subscription_type_by_email(user.email)
        
        # Use appropriate plan based on subscription
        if subscription_status == 'active':
            plan = subscription_type if subscription_type in settings.SUBSCRIPTION_PLANS else 'free'
        else:
            plan = 'free'
            
        plan_limits = cls.get_plan_limits(plan)
        plan_name = settings.SUBSCRIPTION_PLAN_NAMES.get(plan, 'Free')
        
        # Count organizations (excluding personal)
        current_org_count = Organization.objects.filter(
            owner=user
        ).exclude(
            id=user.personal_organization.id if user.personal_organization else None
        ).count()
        
        if current_org_count >= plan_limits['max_orgs']:
            raise ValidationError(
                f"You have reached the maximum organization limit of {plan_limits['max_orgs']} "
                f"for the {plan_name} plan"
            )
        return True


class OrganizationMember(NBaseModel):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('member', 'Member'),
    )

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_memberships',
        null=True,
        blank=True
    )
    invitation_email = models.EmailField(null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='member'
    )
    invitation_accepted = models.BooleanField(default=False)

    def __str__(self):
        if self.user:
            return f"{self.user} - {self.organization} ({self.role})"
        return f"{self.invitation_email} - {self.organization} ({self.role})"
