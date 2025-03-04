"""
Django settings for unstruct_backend project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""

# flake8: noqa

import os
from datetime import timedelta
from pathlib import Path

import environ

# Initialize environ
env = environ.Env()

# Determine the base directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Read .env file
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

env = environ.Env()

# reading the EVN file
environ.Env.read_env(BASE_DIR.__str__() + "/../.env")

# SECURITY WARNING: keep the secret key used in production secret!
# Raises django's ImproperlyConfigured exception if SECRET_KEY not in os.environ
SECRET_KEY = env("SECRET_KEY")

# Set Cognito authentication flag from environment variable ENABLE_COGNITO_AUTH (default True)
ENABLE_COGNITO_AUTH = env.bool("ENABLE_COGNITO_AUTH", default=True)

# Stripe Settings
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')

# Subscription Plan Names - Configurable through env
SUBSCRIPTION_PLAN_NAMES = {
    'free': env('FREE_PLAN_NAME', default='Free'),
    'pro': env('PRO_PLAN_NAME', default='Pro'),
    'enterprise': env('ENTERPRISE_PLAN_NAME', default='Enterprise')
}

# Subscription Plan Limits
SUBSCRIPTION_PLANS = {
    'free': {
        'max_orgs': env.int('FREE_PLAN_MAX_ORGS', default=1),
        'max_members': env.int('FREE_PLAN_MAX_MEMBERS', default=5),
        'max_pdfs_per_month': env.int('FREE_PLAN_MAX_PDFS', default=10),
        'max_video_gb_per_month': env.float('FREE_PLAN_MAX_VIDEO_GB', default=0.5),  # 500MB
        'max_audio_gb_per_month': env.float('FREE_PLAN_MAX_AUDIO_GB', default=0.5)   # 500MB
    },
    'pro': {
        'max_orgs': env.int('PRO_PLAN_MAX_ORGS', default=5),
        'max_members': env.int('PRO_PLAN_MAX_MEMBERS', default=10),
        'max_pdfs_per_month': env.int('PRO_PLAN_MAX_PDFS', default=100),
        'max_video_gb_per_month': env.float('PRO_PLAN_MAX_VIDEO_GB', default=5.0),   # 5GB
        'max_audio_gb_per_month': env.float('PRO_PLAN_MAX_AUDIO_GB', default=5.0)    # 5GB
    },
    'enterprise': {
        'max_orgs': env.int('ENTERPRISE_PLAN_MAX_ORGS', default=999999),
        'max_members': env.int('ENTERPRISE_PLAN_MAX_MEMBERS', default=999999),
        'max_pdfs_per_month': env.int('ENTERPRISE_PLAN_MAX_PDFS', default=999999),
        'max_video_gb_per_month': env.float('ENTERPRISE_PLAN_MAX_VIDEO_GB', default=999999.0),
        'max_audio_gb_per_month': env.float('ENTERPRISE_PLAN_MAX_AUDIO_GB', default=999999.0)
    }
}

# Additional plans can be added through env vars
ADDITIONAL_PLANS = env.dict('ADDITIONAL_PLANS', default={})
if ADDITIONAL_PLANS:
    for plan_name, plan_config in ADDITIONAL_PLANS.items():
        SUBSCRIPTION_PLANS[plan_name] = {
            'max_orgs': env.int(f'{plan_name.upper()}_MAX_ORGS', default=1),
            'max_members': env.int(f'{plan_name.upper()}_MAX_MEMBERS', default=5),
            'max_pdfs_per_month': env.int(f'{plan_name.upper()}_MAX_PDFS', default=10),
            'max_video_gb_per_month': env.float(f'{plan_name.upper()}_MAX_VIDEO_GB', default=0.5),
            'max_audio_gb_per_month': env.float(f'{plan_name.upper()}_MAX_AUDIO_GB', default=0.5)
        }
        SUBSCRIPTION_PLAN_NAMES[plan_name] = env(f'{plan_name.upper()}_PLAN_NAME', default=plan_name.title())

# All available plan choices for the Organization model
SUBSCRIPTION_PLAN_CHOICES = [(k, v) for k, v in SUBSCRIPTION_PLAN_NAMES.items()]

# Frontend URL Configuration
FRONTEND_URL = env.str('FRONTEND_URL', default='http://localhost:3000')

# Application definition

UNSTRUCT_APPS = [
    "apps.common",
    "apps.core",
    "apps.agent_management",
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "rest_framework",
    "rest_framework.authtoken",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.amazon_cognito",
    "dj_rest_auth.registration",
    "corsheaders",
    'drf_spectacular',
] + UNSTRUCT_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",  # Allauth middleware
]

# django-allauth configurations
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",  # new
]

SOCIALACCOUNT_PROVIDERS = {
    "amazon_cognito": {
        "DOMAIN": "[REPLACE THIS]https://<domain-prefix>.auth.us-east-1.amazoncognito.com",
    }
}

SITE_ID = 1

ACCOUNT_EMAIL_VERIFICATION = "none"  # new

ROOT_URLCONF = "apps.urls"

LOGIN_REDIRECT_URL = "/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='unstruct_prod'),
        'USER': env('DB_USER', default='unstructadmin'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default=''),
        'PORT': env('DB_PORT', default='5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_USER_MODEL = "core.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Pagination
REST_FRAMEWORK = {"DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination", "PAGE_SIZE": 100}

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")

# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "apps.common.auth.simple_auth.SimpleAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "dj_rest_auth.jwt_auth.JWTCookieAuthentication",
    ),
    #"DEFAULT_SCHEMA_CLASS": "rest_framework.schemas.coreapi.AutoSchema",
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',

}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(minutes=20),
}

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_COOKIE": "unstruct-app-auth",
    "JWT_AUTH_REFRESH_COOKIE": "my-refresh-token",
}

# Google Drive Settings
GOOGLE_DRIVE_SERVICE_ACCOUNT = None  # This will be overridden by environment-specific settings
GOOGLE_DRIVE_CREDENTIALS = {
    'token_uri': 'https://oauth2.googleapis.com/token',
    'client_id': env('GOOGLE_CLIENT_ID', default=''),
    'client_secret': env('GOOGLE_CLIENT_SECRET', default=''),
    'scopes': ['https://www.googleapis.com/auth/drive.readonly']
}

# AWS Cognito Settings
USER_POOL_ID = env('USER_POOL_ID', default='')
AWS_REGION = env('AWS_REGION', default='')
USER_POOL_CLIENT_ID = env('USER_POOL_CLIENT_ID', default='')

# Logging configuration

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{asctime} {levelname} {filename} {funcName} {lineno} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{asctime} {levelname} - {message}",
            "style": "{",
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse",
        },
        "require_debug_true": {
            "()": "django.utils.log.RequireDebugTrue",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "filters": ["require_debug_true"],
            "formatter": "simple",
        },
        "log_file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "api.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 mb
            "backupCount": 5,
            "formatter": "verbose",
        },
        "error_file": {
            "level": "ERROR",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "api_error.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 mb
            "backupCount": 5,
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
            "filters": ["require_debug_false"],
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django_project_api": {
            "handlers": ["console", "log_file", "error_file", "mail_admins"],
            "level": "DEBUG",
        },
        "django.request": {
            "handlers": ["mail_admins", "error_file"],
            "level": "ERROR",
            "propagate": False,
        },
    },
}

# Add these configurations
AI_MODEL = env("AI_MODEL", default="Gemini") # or other models when integrated
OPENAI_API_KEY = env("OPENAI_API_KEY", default='')

GEMINI_API_KEY = env("GEMINI_API_KEY", default='')

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ['*']
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
    'x-user-email',
    'x-organization-id',
]


# Google OAuth Settings
GOOGLE_CLIENT_ID = env("GOOGLE_CLIENT_ID", default='')
GOOGLE_CLIENT_SECRET = env("GOOGLE_CLIENT_SECRET", default='')

# Session Settings
SESSION_COOKIE_SECURE = False
SESSION_COOKIE_SAMESITE = None
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_SAMESITE = None
CSRF_TRUSTED_ORIGINS = ["http://localhost:3000"]
CSRF_USE_SESSIONS = True
CSRF_COOKIE_HTTPONLY = True

# Add near the top of the file, after the imports
def get_api_base_url():
    """Get the base URL for the API based on environment settings"""
    protocol = env("API_PROTOCOL", default="http")
    host = env("API_HOST", default="localhost")
    port = env("API_PORT", default="8000")
    stage = env("API_STAGE", default="")
    
    if env("DJANGO_ENV", default="development") == 'production':
        base_url = f"{protocol}://{host}"
        if stage:
            base_url = f"{base_url}/{stage}"
        return base_url
    return f"{protocol}://{host}:{port}"

# Add this with your other Google settings
GOOGLE_OAUTH_REDIRECT_URI = f"{get_api_base_url()}/core/google-drive/callback/"

# Add this to your settings file
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')

