from allauth.socialaccount.providers.amazon_cognito.views import AmazonCognitoOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from django.conf import settings
from django.middleware.csrf import get_token
import os
import json


class CognitoLoginView(SocialLoginView):
    adapter_class = AmazonCognitoOAuth2Adapter
    callback_url = "http://localhost:8000/dj-rest-auth/cognito/"
    client_class = OAuth2Client


class GoogleDriveAuthView(APIView):
    """Handle Google Drive OAuth2 flow"""
    
    def get(self, request):
        """Initiate OAuth2 flow and return authorization URL"""
        try:
            # Create OAuth2 flow instance
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost:3000/api/auth/callback/google"]
                    }
                },
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            
            # Generate authorization URL
            authorization_url, state = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                prompt='consent'
            )
            
            # Store state in session
            request.session['google_oauth_state'] = state
            
            # Get CSRF token
            csrf_token = get_token(request)
            
            response = Response({
                "authorization_url": authorization_url,
                "state": state,
                "csrf_token": csrf_token
            })
            
            # Set CORS headers
            response["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response["Access-Control-Allow-Credentials"] = "true"
            
            return response
            
        except Exception as e:
            return Response(
                {"error": f"Failed to initiate Google Drive OAuth flow: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class GoogleDriveCallbackView(APIView):
    """Handle Google Drive OAuth2 callback"""
    
    def post(self, request):
        """Handle OAuth2 callback and return tokens"""
        try:
            # Get authorization code from request
            code = request.data.get('code')
            if not code:
                return Response(
                    {"error": "No authorization code received"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Create OAuth2 flow instance
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": ["http://localhost:3000/api/auth/callback/google"]
                    }
                },
                scopes=['https://www.googleapis.com/auth/drive.readonly']
            )
            
            # Set the redirect URI
            flow.redirect_uri = "http://localhost:3000/api/auth/callback/google"
            
            # Exchange authorization code for tokens
            flow.fetch_token(code=code)
            
            # Get credentials
            credentials = flow.credentials
            
            response = Response({
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "client_secret": credentials.client_secret,
                "scopes": credentials.scopes
            })
            
            # Set CORS headers
            response["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response["Access-Control-Allow-Credentials"] = "true"
            
            return response
            
        except Exception as e:
            return Response(
                {"error": f"Failed to complete Google Drive OAuth flow: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
    def options(self, request):
        """Handle preflight requests"""
        response = Response()
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
