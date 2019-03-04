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
    'project',
    'auth_ex',
    'manager',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django_extensions',
    'crispy_forms',
] + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # TODO add referrer policy
]

ROOT_URLCONF = 'project.urls'
WSGI_APPLICATION = 'project.wsgi.application'

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


# ----------------------- AUTH ----------------------------------


AUTH_USER_MODEL = 'auth_ex.User'
LOGIN_URL = 'auth:login'
LOGIN_REDIRECT_URL = 'homepage'
LOGOUT_REDIRECT_URL = 'homepage'
MFA_APPLICATION_NAME = 'DjangoButtermilk'

PASSWORD_HASHERS = [
    'project.utils.Argon2PasswordHasher',
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


# ---------------------------------------------------------------

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True


STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'  # noqa
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

SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_SAMESITE = 'Strict'

CSRF_COOKIE_SAMESITE = 'Strict'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

RECAPTCHA_PUBLIC_KEY = env('RECAPTCHA_PUBLIC_KEY', default='')
RECAPTCHA_PRIVATE_KEY = env('RECAPTCHA_PRIVATE_KEY', default='')

GEOIP_PATH = env('GEOIP_PATH', default=root('project/geolite2/'))
