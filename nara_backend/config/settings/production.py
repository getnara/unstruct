from .base import *  # noqa: F401 F403
import os

# SECURITY WARNING: don't run with debug turned on in production!

DEBUG = False
ALLOWED_HOSTS = ["*"]

CORS_ALLOW_ALL_ORIGINS = True

# Security settings
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'apps.common.auth': {  # This will capture logs from our authentication module
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'apps.core.views': {  # This will capture logs from our core views
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# AWS S3 Configuration
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION = os.environ.get('AWS_S3_REGION', 'us-east-2')

# Database Configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'nara_prod',
        'USER': 'naraadmin',
        'PASSWORD': 'Nara2024!Secure',
        'HOST': 'nara-prod.cbaoiyyw8szg.us-east-2.rds.amazonaws.com',
        'PORT': '5432',
    }
}
