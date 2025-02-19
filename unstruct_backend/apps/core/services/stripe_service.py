import stripe
import logging
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class StripeService:
    def __init__(self):
        self.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_key = self.api_key

    def get_subscription_status_by_email(self, email):
        """Get subscription status for a customer by email"""
        if not self.api_key:
            logger.info(f"Stripe API key is empty. Skipping subscription status check for email: {email}")
            return None

        try:
            logger.info(f"Checking subscription status for email: {email}")
            
            # Find customer by email
            customers = stripe.Customer.list(email=email, limit=1)
            if not customers.data:
                logger.info(f"No Stripe customer found for email: {email}")
                return None
                
            customer = customers.data[0]
            logger.info(f"Found Stripe customer: {customer.id}")
            
            # Get active subscriptions for the customer
            subscriptions = stripe.Subscription.list(
                customer=customer.id,
                status='active',
                limit=1
            )
            
            if subscriptions.data:
                logger.info(f"Found active subscription for customer: {customer.id}")
                return 'active'
            
            logger.info(f"No active subscriptions found for customer: {customer.id}")
            return None
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error checking subscription status: {str(e)}")
            return None

    def get_subscription_info_by_email(self, email):
        """Get subscription period information for a customer by email"""
        if not self.api_key:
            logger.info(f"Stripe API key is empty. Skipping subscription info retrieval for email: {email}")
            return None

        try:
            logger.info(f"Getting subscription info for email: {email}")
            
            # Find customer by email
            customers = stripe.Customer.list(email=email, limit=1)
            if not customers.data:
                logger.info(f"No Stripe customer found for email: {email}")
                return None
                
            customer = customers.data[0]
            logger.info(f"Found Stripe customer: {customer.id}")
            
            # Get active subscriptions for the customer
            subscriptions = stripe.Subscription.list(
                customer=customer.id,
                status='active',
                limit=1
            )
            
            if not subscriptions.data:
                logger.info(f"No active subscriptions found for customer: {customer.id}")
                return None
            
            subscription = subscriptions.data[0]
            
            # Convert timestamps to datetime
            current_period_start = timezone.datetime.fromtimestamp(
                subscription.current_period_start, 
                tz=timezone.get_current_timezone()
            )
            current_period_end = timezone.datetime.fromtimestamp(
                subscription.current_period_end,
                tz=timezone.get_current_timezone()
            )
            
            return {
                'current_period_start': current_period_start,
                'current_period_end': current_period_end,
                'subscription_id': subscription.id
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error getting subscription info: {str(e)}")
            return None

    def get_subscription_type_by_email(self, email):
        """Get subscription type for a customer by email"""
        if not self.api_key:
            logger.info(f"Stripe API key is empty. Skipping subscription type check for email: {email}")
            return 'free'

        try:
            logger.info(f"Checking subscription type for email: {email}")
            
            # Find customer by email
            customers = stripe.Customer.list(email=email, limit=1)
            if not customers.data:
                logger.info(f"No Stripe customer found for email: {email}")
                return 'free'
                
            customer = customers.data[0]
            logger.info(f"Found Stripe customer: {customer.id}")
            
            # Get active subscriptions for the customer
            subscriptions = stripe.Subscription.list(
                customer=customer.id,
                status='active',
                limit=1,
                expand=['data.plan.product']
            )
            
            if not subscriptions.data:
                logger.info(f"No active subscriptions found for customer: {customer.id}")
                return 'free'
                
            # Get the subscription type from the product name
            subscription = subscriptions.data[0]
            product = subscription.plan.product
            product_name = product.name.lower()
            
            logger.info(f"Product name: {product_name}")
            
            # Match product name with available plans
            for plan_name in settings.SUBSCRIPTION_PLAN_NAMES.keys():
                if settings.SUBSCRIPTION_PLAN_NAMES[plan_name].lower() == product_name:
                    return plan_name
            
            # If no match found, return free plan
            return 'free'
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error checking subscription type: {str(e)}")
            return 'free' 