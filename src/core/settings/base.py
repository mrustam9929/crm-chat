import os
from pathlib import Path

# region DJANGO_SETTINGS
BASE_DIR = Path(__file__).resolve().parent.parent.parent

DJANGO = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]
APPS = [
    'apps.users',
    'apps.chat',
]
LIBS = [
    'channels',
    'corsheaders',
    'rest_framework',
    'drf_yasg',
    'django_ckeditor_5',
    'django_filters'
]
INSTALLED_APPS = DJANGO + LIBS + APPS

WSGI_APPLICATION = 'core.wsgi.application'
ROOT_URLCONF = 'core.urls'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# endregion

# region CORS headers
CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = os.getenv(
    'CSRF_TRUSTED_ORIGINS', 'http://localhost'
).split(' ')
# endregion


# region DATABASES
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.getenv('DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_HOST'),
        'PORT': os.getenv('DB_PORT'),
    }
}
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', 6379)
# endregion

# region CACHE

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": f'redis://{REDIS_HOST}:{REDIS_PORT}/1',
        "KEY_PREFIX": "lms_chat_cache"
    }
}
USER_CHANNELS_CACHE_KEY = "user_channels_names_{user_id}"
USER_CHANNELS_CACHE_TIMEOUT = 60
# endregion

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# region INTERNATIONALIZATION
LANGUAGE_CODE = 'ru'
TIME_ZONE = "UTC"
USE_I18N = True
USE_L10N = True
USE_TZ = True
# endregion

AUTH_USER_MODEL = 'users.User'

# region REST_FRAMEWORK_SETTINGS
SWAGGER_SETTINGS = {
    'SECURITY_DEFINITIONS': {
        'Bearer': {'type': 'apiKey', 'name': 'Authorization', 'in': 'header'}
    },
    'DEFAULT_MODEL_RENDERING': 'example'
}
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.AllowAny',),
    'DEFAULT_AUTHENTICATION_CLASSES': (),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10
}
# endregion

CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': ['heading', '|', 'bold', 'italic', 'link',
                    'bulletedList', 'numberedList', 'blockQuote', 'imageUpload', ],

    },
}

# region CONSTANTS
CHAT_MESSAGE_FILE_MAX_SIZE = int(os.getenv('CHAT_MESSAGE_FILE_MAX_SIZE', 50))  # MB
CHAT_MESSAGE_ALLOWED_FILE_EXTENSIONS = os.getenv(
    'CHAT_MESSAGE_ALLOWED_FILE_EXTENSIONS', 'xls,xlsx,doc,docx,pdf,jpg,png,pptx,mp4,avi,3gpp'
).split(',')
# endregion


# region CHANNELS_SETTINGS
ASGI_APPLICATION = "core.asgi.application"
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(REDIS_HOST, REDIS_PORT), ]
        },
    },
}

# endregion

# region KEYCLOAK_SETTINGS
KEYCLOAK_SERVER_URL = os.getenv('KEYCLOAK_SERVER_URL')
KEYCLOAK_CLIENT_ID = os.getenv('KEYCLOAK_CLIENT_ID')
KEYCLOAK_PUBLIC_KEY = os.getenv('KEYCLOAK_PUBLIC_KEY')
KEYCLOAK_REALM_NAME = os.getenv('KEYCLOAK_REALM_NAME')
KEYCLOAK_CLIENT_SECRET_KEY = os.getenv('KEYCLOAK_CLIENT_SECRET_KEY')

KEYCLOAK_CLIENT_ROLE = os.getenv('KEYCLOAK_CLIENT_ROLE', 'chat_user')
KEYCLOAK_CURATOR_ROLE = os.getenv('KEYCLOAK_CURATOR_ROLE', 'chat_manager')
# endregion
