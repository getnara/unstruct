from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import Flow
from django.conf import settings
from django.http import HttpResponse
import os
import json
import logging

# Configure logger
logger = logging.getLogger(__name__)

def get_api_base_url():
    """Get the base URL for the API based on environment settings"""
    protocol = settings.API_PROTOCOL
    host = settings.API_HOST
    port = settings.API_PORT
    
    # In production, we might not need to include the port
    if settings.DJANGO_ENV == 'production':
        return f"{protocol}://{host}"
    return f"{protocol}://{host}:{port}"

# Configuration for supported file types - easy to update in batches
SUPPORTED_FILE_TYPES = {
    'folders': ['application/vnd.google-apps.folder'],
    'pdf': [
        'application/pdf',
        'application/x-pdf',
        'application/acrobat',
        'applications/vnd.pdf',
        'text/pdf',
        'text/x-pdf'
    ],
    # Ready for future batches
    # 'documents': [
    #     'application/vnd.google-apps.document',
    #     'application/msword',
    #     'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    # ],
    # 'spreadsheets': [...],
}

class GoogleDriveFilesView(APIView):
    """Handle Google Drive file listing"""
    permission_classes = [AllowAny]  # Allow unauthenticated access
    authentication_classes = []  # Disable DRF authentication
    
    def options(self, request, *args, **kwargs):
        """Handle preflight CORS requests"""
        response = Response()
        response["Access-Control-Allow-Origin"] = settings.FRONTEND_URL
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
    
    def post(self, request):
        """List files in a Google Drive folder"""
        try:
            # Debug: Log complete request details
            logger.info("=== Request Debug Information ===")
            logger.info(f"Request Method: {request.method}")
            logger.info(f"Request Path: {request.path}")
            logger.info(f"Request Origin: {request.headers.get('origin', 'No origin')}")
            logger.info(f"CORS Headers Present:")
            logger.info(f"  Access-Control-Request-Method: {request.headers.get('access-control-request-method')}")
            logger.info(f"  Access-Control-Request-Headers: {request.headers.get('access-control-request-headers')}")
            
            # Log all headers for debugging
            all_headers = {k: v for k, v in request.headers.items()}
            logger.info(f"All Request Headers: {all_headers}")
            
            # Get the Google token from Authorization header
            auth_header = request.headers.get('Authorization')
            google_token = None
            
            if auth_header and auth_header.startswith('Bearer '):
                google_token = auth_header.split(' ')[1]
            
            # Debug: Log token information
            logger.info("=== Token Debug Information ===")
            logger.info(f"Authorization header present: {bool(auth_header)}")
            if google_token:
                logger.info(f"Token length: {len(google_token)}")
                logger.info(f"Token type: {auth_header.split(' ')[0] if auth_header else 'None'}")
                logger.info(f"Token preview: {google_token[:10]}...")
            
            if not google_token:
                # Debug: Log all potential auth headers
                logger.error("=== Missing Token Debug ===")
                auth_headers = {
                    k: v for k, v in request.headers.items() 
                    if k.lower().startswith(('x-', 'authorization'))
                }
                logger.error(f"All auth-related headers: {auth_headers}")
                logger.error(f"CORS headers present: {bool(request.headers.get('origin'))}")
                return Response(
                    {"error": "No Google access token provided"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Get the folder ID from request data
            folder_id = request.data.get('folderId', 'root')
            logger.info(f"Fetching files for folder: {folder_id}")
            
            try:
                # Create credentials object
                credentials = Credentials(
                    token=google_token,
                    token_uri="https://oauth2.googleapis.com/token",
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET,
                    scopes=['https://www.googleapis.com/auth/drive.readonly']
                )
                
                # Create Drive API service
                service = build('drive', 'v3', credentials=credentials)
                
                # Build query for enabled file types
                enabled_types = SUPPORTED_FILE_TYPES['folders'] + SUPPORTED_FILE_TYPES['pdf']
                type_conditions = [f"mimeType = '{mime_type}'" for mime_type in enabled_types]
                type_query = " or ".join(type_conditions)
                
                query = f"'{folder_id}' in parents and ({type_query}) and trashed = false"
                
                results = service.files().list(
                    q=query,
                    fields="files(id, name, mimeType, size, modifiedTime)",
                    orderBy="folder,name"
                ).execute()
                
                logger.info(f"Successfully fetched {len(results.get('files', []))} files")
                
                # Add CORS headers to the response
                response = Response({"files": results.get('files', [])})
                response["Access-Control-Allow-Origin"] = settings.FRONTEND_URL
                response["Access-Control-Allow-Headers"] = "Content-Type, X-Google-Token"
                response["Access-Control-Allow-Credentials"] = "true"
                return response
                
            except Exception as e:
                logger.error(f"Error using Google token: {str(e)}", exc_info=True)
                return Response(
                    {"error": "Invalid or expired Google token"},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
        except Exception as e:
            logger.error(f"=== Error Debug Information ===")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error message: {str(e)}")
            logger.exception("Full traceback:")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GoogleDriveAuthView(APIView):
    """Handle Google Drive OAuth authorization"""
    
    DRIVE_SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.metadata.readonly'
    ]
    
    def get(self, request):
        """Get authorization URL for Google Drive"""
        try:
            # Use the configured redirect URI from settings
            redirect_uri = settings.GOOGLE_OAUTH_REDIRECT_URI
            
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                },
                scopes=self.DRIVE_SCOPES,
                redirect_uri=redirect_uri
            )
            
            auth_url = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )[0]
            
            return Response({"authorization_url": auth_url})
            
        except Exception as e:
            logger.error(f"Error generating auth URL: {str(e)}", exc_info=True)
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class GoogleDriveCallbackView(APIView):
    """Handle Google Drive OAuth callback"""
    
    DRIVE_SCOPES = [
        'https://www.googleapis.com/auth/drive.readonly',
        'https://www.googleapis.com/auth/drive.metadata.readonly'
    ]
    
    def get(self, request):
        """Handle the OAuth callback and return tokens via window.postMessage"""
        try:
            code = request.GET.get('code')
            state = request.GET.get('state')
            
            if not code:
                return self._return_error_html("No authorization code provided")
            
            logger.info(f"Received callback with code: {code[:10]}... and state: {state}")
            
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": settings.GOOGLE_CLIENT_ID,
                        "client_secret": settings.GOOGLE_CLIENT_SECRET,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                    }
                },
                scopes=self.DRIVE_SCOPES,
                redirect_uri=settings.GOOGLE_OAUTH_REDIRECT_URI
            )
            
            flow.oauth2session.scope = request.GET.get('scope', '').split(' ')
            
            try:
                flow.fetch_token(code=code)
            except Warning as w:
                logger.warning(f"OAuth warning (continuing): {str(w)}")
            except Exception as e:
                raise e
            
            # Get the credentials
            credentials = flow.credentials
            
            logger.info("Successfully exchanged code for tokens")
            
            # Create success response HTML with debugging
            response_data = {
                "type": "oauth_complete",
                "access_token": credentials.token,
                "refresh_token": credentials.refresh_token,
                "token_uri": credentials.token_uri,
                "client_id": credentials.client_id,
                "scopes": credentials.scopes
            }

            # Get the frontend origin from Django settings
            frontend_origin = settings.FRONTEND_URL
            
            html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>OAuth Callback</title>
                    <script>
                        console.log('OAuth callback page loaded');
                        
                        function sendMessageAndClose() {{
                            console.log('Starting sendMessageAndClose');
                            const message = {json.dumps(response_data)};
                            const targetOrigin = '{frontend_origin}';
                            
                            console.log('Message to send:', message);
                            console.log('Target origin:', targetOrigin);
                            
                            if (window.opener) {{
                                try {{
                                    console.log('Found opener window, sending message');
                                    window.opener.postMessage(message, targetOrigin);
                                    console.log('Message sent successfully');
                                    
                                    // Close window after a short delay
                                    setTimeout(() => {{
                                        console.log('Attempting to close window');
                                        window.close();
                                        
                                        // If window didn't close, show close button
                                        setTimeout(() => {{
                                            if (!window.closed) {{
                                                document.getElementById('closeButton').style.display = 'block';
                                            }}
                                        }}, 500);
                                    }}, 1000);
                                }} catch (error) {{
                                    console.error('Error sending message:', error);
                                    document.getElementById('status').textContent = 'Error: ' + error.message;
                                    document.getElementById('closeButton').style.display = 'block';
                                }}
                            }} else {{
                                console.error('No opener window found');
                                document.getElementById('status').textContent = 'Error: No opener window found';
                                document.getElementById('closeButton').style.display = 'block';
                            }}
                        }}

                        // Try to send message immediately
                        sendMessageAndClose();
                        
                        // Also try when the page is fully loaded
                        window.addEventListener('load', sendMessageAndClose);
                    </script>
                </head>
                <body style="text-align: center; padding: 20px; font-family: Arial, sans-serif;">
                    <h3>Authentication Complete</h3>
                    <p id="status">Closing window...</p>
                    <button id="closeButton" 
                            onclick="window.close()" 
                            style="display: none; padding: 10px 20px; margin-top: 20px; cursor: pointer;">
                        Close Window
                    </button>
                </body>
                </html>
            """
            
            response = HttpResponse(html_content)
            response["Cross-Origin-Opener-Policy"] = "unsafe-none"
            response["Cross-Origin-Embedder-Policy"] = "unsafe-none"
            response["Access-Control-Allow-Origin"] = frontend_origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
            response["Content-Security-Policy"] = "default-src 'self' 'unsafe-inline'; script-src 'unsafe-inline' 'self'; connect-src *;"
            return response
            
        except Exception as e:
            logger.error(f"Error in OAuth callback: {str(e)}")
            return self._return_error_html(f"Authentication failed: {str(e)}")
            
    def _return_error_html(self, error_message: str) -> HttpResponse:
        frontend_origin = settings.FRONTEND_URL
        html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>OAuth Error</title>
                <script>
                    function sendErrorAndClose() {{
                        try {{
                            if (window.opener) {{
                                window.opener.postMessage({{
                                    type: 'oauth_error',
                                    error: '{error_message}'
                                }}, '{frontend_origin}');
                                setTimeout(() => window.close(), 100);
                            }} else {{
                                document.body.innerHTML = '<h3>Authentication Error</h3><p>{error_message}</p><p>You can now close this window and try again.</p>';
                            }}
                        }} catch (error) {{
                            console.error('Failed to send error:', error);
                            document.body.innerHTML = '<h3>Authentication Error</h3><p>{error_message}</p><p>You can now close this window and try again.</p>';
                        }}
                    }}

                    // Try to send error as soon as possible
                    sendErrorAndClose();
                </script>
            </head>
            <body>
                <h3>Authentication Error</h3>
                <p>Closing window...</p>
            </body>
            </html>
        """
        response = HttpResponse(html_content)
        response["Cross-Origin-Opener-Policy"] = "unsafe-none"
        response["Cross-Origin-Embedder-Policy"] = "unsafe-none"
        response["Access-Control-Allow-Origin"] = frontend_origin
        response["Access-Control-Allow-Credentials"] = "true"
        return response