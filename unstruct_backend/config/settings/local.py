import os
from .base import *  # noqa: F401 F403

# Database Configuration for Local Development
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='unstruct_local'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default='postgres'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = True
ALLOWED_HOSTS = ["*"]

INTERNAL_IPS = [
    "127.0.0.1",
]

# Google Drive Service Account
GOOGLE_DRIVE_SERVICE_ACCOUNT = {
    "type": "service_account",
    "project_id": "your-project-id",  # Replace with your project ID
    "private_key_id": "your-private-key-id",  # Replace with your private key ID
    "private_key": "-----BEGIN PRIVATE KEY-----\nYour-Private-Key\n-----END PRIVATE KEY-----\n",  # Replace with your private key
    "client_email": "your-service-account@your-project.iam.gserviceaccount.com",  # Replace with your service account email
    "client_id": "your-client-id",  # Replace with your client ID
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"  # Replace with your cert URL
}

# AWS S3 Configuration
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME', '')
AWS_S3_REGION = "us-east-2"
