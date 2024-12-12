from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from apps.core.models.user import User
from django.conf import settings
from pycognito import Cognito
from pycognito.exceptions import TokenVerificationException

class SimpleAuthentication(BaseAuthentication):
    """Authentication class that validates Cognito tokens and creates/gets users"""
    
    def authenticate(self, request):
        # Get the token from the Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            # Extract the token
            token_type, token = auth_header.split()
            if token_type.lower() != 'bearer':
                return None

            # Initialize Cognito object
            cognito = Cognito(
                user_pool_id=settings.USER_POOL_ID,
                client_id=settings.USER_POOL_CLIENT_ID,
                user_pool_region=settings.AWS_REGION
            )
            
            # Verify the token
            claims = cognito.verify_token(
                token=token,
                token_use="id",  # Using ID token to get email
                id_name="access_token"
            )
            
            # Get email from token claims
            email = claims.get('email')
            if not email:
                raise AuthenticationFailed('No email found in token')
            
            # Get or create user based on email
            user, _ = User.objects.get_or_create(
                email=email,
                defaults={
                    'username': email,
                    'is_active': True
                }
            )
            
            return (user, None)

        except (ValueError, TokenVerificationException) as e:
            print(f"Token validation failed: {str(e)}")
            return None
        except Exception as e:
            print(f"Authentication error: {str(e)}")
            return None

    def authenticate_header(self, request):
        return 'Bearer'
