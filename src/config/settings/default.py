import environ
import os
import re


class DockerEnv(environ.Env):
    # Author: Mateusz Kamycki https://github.com/toffi9

    def get_value(self, var, *args, **kwargs):
        value = super().get_value(var, *args, **kwargs)

        if isinstance(value, str):
            # is file path is format like `/run/secrets/test_secret`
            is_file_path_of_secret = re.match(r'^\/run\/secrets\/\w+$', value)
            secret_file_exists = os.path.exists(value)
            if is_file_path_of_secret and secret_file_exists:
                value = self.get_value_from_secret_file(value)

        return value

    def get_value_from_secret_file(self, value):
        with open(value, 'r') as secret_file:
            # rstrip for deleting all new lines
            return secret_file.read().rstrip('\r\n')


env = DockerEnv()
root = environ.Path(__file__) - 3

BASE_DIR = root()
SECRET_KEY = env('SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)
SITE_ID = env.int('SITE_ID', default=1)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost'])

LOCAL_APPS = [
    'config',
    'auth_ex',
    'users',
    'manager',
]

INSTALLED_APPS = [
    'config.apps.AdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',
    'crispy_forms',
    'rest_framework',
] + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'auth_ex.middleware.DeviceCookieMiddleware',
    # TODO add referrer policy
]

ROOT_URLCONF = 'config.urls'
WSGI_APPLICATION = 'config.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [root('templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

CRISPY_TEMPLATE_PACK = 'bootstrap4'


DATABASES = {
    'default': env.db(
        default='postgres://postgres:postgres@postgres:5432/postgres'
    )
}

CACHEOPS_ENABLED = env.bool('CACHEOPS_ENABLED', default=True)
CACHEOPS_REDIS = env('CACHE_REDIS_URL', default='redis://redis:6379/1')
CACHEOPS_DEGRADE_ON_FAILURE = True
CACHEOPS_DEFAULTS = {'timeout': 60 * 60}
CACHEOPS = {}


# ------------------------ API ----------------------------------

REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'URL_FORMAT_OVERRIDE': None,
    'FORMAT_SUFFIX_KWARG': None,
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAdminUser',
    ],
    # Versioning
    'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
    'DEFAULT_VERSION': 'v1',
    'ALLOWED_VERSIONS': ('v1',),
    # Pagination
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    # Filtering & Ordering
    'SEARCH_PARAM': 'q',
    'ORDERING_PARAM': 'order',
}


# ----------------------- AUTH ----------------------------------


AUTH_USER_MODEL = 'users.User'
LOGIN_URL = 'auth:login'
LOGIN_REDIRECT_URL = 'homepage'
LOGOUT_REDIRECT_URL = 'homepage'
MFA_APPLICATION_NAME = 'ButtermilkSecurity'

PASSWORD_HASHERS = [
    'auth_ex.hashers.Argon2PasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',  # noqa
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # noqa
        'OPTIONS': {
            'min_length': 12,
        }
    },
    {
        'NAME': 'auth_ex.validators.ComplexityValidator',
    },
    {
        'NAME': 'auth_ex.validators.HaveIBeenPwnedValidator',
    },
]
PASSWORD_RESET_TIMEOUT_DAYS = 1

AUTHENTICATION_BACKENDS = [
    'auth_ex.backends.ModelBackend',
]

# Changing session's cookie name to mislead potential attacker
SESSION_COOKIE_NAME = 'PHPSESSID'  # :D

# Session expires when users leaves the browser
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Cookie won't be sent in cross-origin requests
SESSION_COOKIE_SAMESITE = 'Strict'

# Cookie won't be sent in cross-origin requests
CSRF_COOKIE_SAMESITE = 'Strict'

# Cookie cannot be accessed with Javascript
CSRF_COOKIE_HTTPONLY = True

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Google reCAPTCHA
RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY', default='')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY', default='')

# Device Cookie - Rate Limiting per device
DEVICE_COOKIE_NAME = 'device-uid'
DEVICE_COOKIE_SALT = env('DEVICE_COOKIE_SALT', default='341eYcyZoWIDF0gP')
DEVICE_COOKIE_PERIOD = 8 * 60 * 60  # 8 hours
DEVICE_COOKIE_TRIES = 10
DEVICE_COOKIE_AGE = 12 * 30 * 24 * 60 * 60  # 360 days


# ---------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATIC_URL = env('STATIC_URL', default='/static/')
STATIC_ROOT = env('STATIC_ROOT', default=(root - 2)('static'))
MEDIA_URL = env('MEDIA_URL', default='/media/')
MEDIA_ROOT = env('MEDIA_ROOT', default=(root - 2)('media'))


EMAIL_BACKEND = env(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='root@localhost')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_PORT = env('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=False)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='root@localhost')

GEOIP_PATH = env('GEOIP_PATH', default=root('config/geolite2/'))
