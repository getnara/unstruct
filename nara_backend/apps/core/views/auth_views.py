from allauth.socialaccount.providers.amazon_cognito.views import AmazonCognitoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView


class CognitoLoginView(SocialLoginView):
    adapter_class = AmazonCognitoOAuth2Adapter
    callback_url = "http://localhost:8000/dj-rest-auth/cognito/"
    client_class = OAuth2Client
