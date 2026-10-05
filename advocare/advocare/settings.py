"""
Django settings for AdvoCare project.

Local development configuration:
- Django REST Framework
- JWT Authentication
- React frontend on localhost:3000
- PostgreSQL on localhost:5432
"""

import os
from pathlib import Path
from datetime import timedelta

from decouple import config
import dj_database_url



# ============================================================
# BASE DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# SECURITY
# ============================================================

# SECRET_KEY = config(
#     "DJANGO_SECRET_KEY",
#     default="django-insecure-development-key-change-this"
# )
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")

# DEBUG = config(
#     "DEBUG",
#     default=True,
#     cast=bool
# )
DEBUG = os.environ.get("DEBUG", "False") == "True"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("ALLOWED_HOSTS", "").split(",")
    if host.strip()
]


# ============================================================
# APPLICATIONS
# ============================================================

INSTALLED_APPS = [

    # Django built-in apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party apps
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "whitenoise.runserver_nostatic",

    # AdvoCare apps
    "users",
    "accounts",
    "profiles",
    "cases",
    "documents",
    "core",
    "dashboards",
    "recommendations",
    "chat",
    "contact",
]


# ============================================================
# MIDDLEWARE
# ============================================================

MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    # Static files
    "whitenoise.middleware.WhiteNoiseMiddleware",

    # CORS
    "corsheaders.middleware.CorsMiddleware",

    # Sessions
    "django.contrib.sessions.middleware.SessionMiddleware",

    # Common middleware
    "django.middleware.common.CommonMiddleware",

    # CSRF protection
    "django.middleware.csrf.CsrfViewMiddleware",

    # Authentication
    "django.contrib.auth.middleware.AuthenticationMiddleware",

    # Django messages
    "django.contrib.messages.middleware.MessageMiddleware",

    # Clickjacking protection
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ============================================================
# URL CONFIGURATION
# ============================================================

ROOT_URLCONF = "advocare.urls"


# ============================================================
# TEMPLATES
# ============================================================

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            os.path.join(BASE_DIR, "frontend", "build"),
        ],

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


# ============================================================
# WSGI
# ============================================================

WSGI_APPLICATION = "advocare.wsgi.application"


# ============================================================
# DATABASE
# ============================================================

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",

#         "NAME": config(
#             "DB_NAME",
#             default="advocare_db"
#         ),

#         "USER": config(
#             "DB_USER",
#             default="postgres"
#         ),

#         "PASSWORD": config(
#             "DB_PASSWORD",
#             default="postgres"
#         ),

#         "HOST": config(
#             "DB_HOST",
#             default="localhost"
#         ),

#         "PORT": config(
#             "DB_PORT",
#             default="5432"
#         ),
#     }
# }

DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get("DATABASE_URL"),
        conn_max_age=600,
    )
}


# ============================================================
# PASSWORD VALIDATION
# ============================================================

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ============================================================
# INTERNATIONALIZATION
# ============================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ============================================================
# STATIC FILES
# ============================================================

STATIC_URL = "/static/"

STATIC_ROOT = os.path.join(
    BASE_DIR,
    "staticfiles"
)

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)


# ============================================================
# MEDIA FILES
# ============================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = os.path.join(
    BASE_DIR,
    "media"
)


# ============================================================
# DEFAULT PRIMARY KEY
# ============================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ============================================================
# CUSTOM USER MODEL
# ============================================================

AUTH_USER_MODEL = "users.User"


# ============================================================
# DJANGO REST FRAMEWORK
# ============================================================

REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),

    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
}


# ============================================================
# JWT CONFIGURATION
# ============================================================

SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME": timedelta(
        minutes=60
    ),

    "REFRESH_TOKEN_LIFETIME": timedelta(
        days=1
    ),

    "AUTH_HEADER_TYPES": (
        "Bearer",
    ),
}


# ============================================================
# CORS
# ============================================================

# CORS_ALLOWED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]

# CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CORS_ALLOWED_ORIGINS",
        ""
    ).split(",")
    if origin.strip()
]


# ============================================================
# CSRF
# ============================================================

# CSRF_TRUSTED_ORIGINS = [
#     "http://localhost:3000",
#     "http://127.0.0.1:3000",
# ]

CSRF_TRUSTED_ORIGINS = [
    origin.strip()
    for origin in os.environ.get(
        "CSRF_TRUSTED_ORIGINS",
        ""
    ).split(",")
    if origin.strip()
]


# ============================================================
# SECURITY SETTINGS
# ============================================================

if not DEBUG:

    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = True

    SESSION_COOKIE_SECURE = True

    CSRF_COOKIE_SECURE = True

    SECURE_CONTENT_TYPE_NOSNIFF = True

    SECURE_BROWSER_XSS_FILTER = True
    