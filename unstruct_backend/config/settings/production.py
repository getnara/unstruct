from .base import *  # noqa: F401 F403
import os
import environ

env = environ.Env()

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
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': env.db(),
    }
else:
    # Fallback to individual environment variables
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='unstruct_prod'),
            'USER': env('DB_USER', default='unstructadmin'),
            'PASSWORD': env('DB_PASSWORD'),
            'HOST': env('DB_HOST', default=''),
            'PORT': env('DB_PORT', default='5432'),
        }
    }
