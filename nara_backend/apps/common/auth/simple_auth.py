from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.core.models.user import User
from django.conf import settings
from pycognito import Cognito
from pycognito.exceptions import TokenVerificationException
import logging

logger = logging.getLogger(__name__)

class SimpleAuthentication(BaseAuthentication):
    """Authentication class that validates Cognito tokens and creates/gets users"""
    
    def authenticate(self, request):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            logger.debug("No Authorization header found")
            return None

        try:
            # Extract the token
            token_type, token = auth_header.split()
            if token_type.lower() != 'bearer':
                logger.debug(f"Unsupported token type: {token_type}")
                return None

            # Initialize Cognito object
            cognito = Cognito(
                user_pool_id=settings.USER_POOL_ID,
                client_id=settings.USER_POOL_CLIENT_ID,
                user_pool_region=settings.AWS_REGION
            )
            
            logger.debug(f"Cognito initialized with pool_id={settings.USER_POOL_ID}, client_id={settings.USER_POOL_CLIENT_ID}, region={settings.AWS_REGION}")
            
            # Verify the token
            claims = cognito.verify_token(
                token=token,
                token_use="id",  # Using ID token
                id_name="id_token"  # This should be id_token for ID tokens
            )
            
            logger.debug(f"Token verified successfully. Claims: {claims}")
            
            # Get email and sub (user ID) from token claims
            email = claims.get('email')
            cognito_user_id = claims.get('sub')
            
            if not email:
                logger.error("No email found in token claims")
                raise AuthenticationFailed('No email found in token')
            
            if not cognito_user_id:
                logger.error("No user ID found in token claims")
                raise AuthenticationFailed('No user ID found in token')

            logger.debug(f"Found email in claims: {email}")
            logger.debug(f"Found user ID in claims: {cognito_user_id}")
            
            # Try to get user by Cognito user ID first
            user = User.objects.filter(id=cognito_user_id).first()
            
            if user:
                # User found by ID, update email if it changed
                if user.email != email:
                    logger.debug(f"Updating email for user {cognito_user_id} from {user.email} to {email}")
                    user.email = email
                    user.save()
            else:
                # Try to find user by email
                user = User.objects.filter(email=email).first()
                if user:
                    # User found by email but has different ID, update their ID
                    logger.debug(f"Updating user ID from {user.id} to {cognito_user_id}")
                    User.objects.filter(id=user.id).update(id=cognito_user_id)
                    user = User.objects.get(id=cognito_user_id)
                else:
                    # Create new user with Cognito user ID
                    logger.debug(f"Creating new user with ID {cognito_user_id} and email {email}")
                    user = User.objects.create(
                        id=cognito_user_id,
                        email=email,
                        username=email,
                        is_active=True
                    )
            
            logger.debug(f"User authenticated with ID: {user.id} and email: {user.email}")
            
            return (user, None)

        except (ValueError, TokenVerificationException) as e:
            logger.error(f"Token validation failed: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None

    def authenticate_header(self, request):
        return 'Bearer'
