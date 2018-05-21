from .default import *  # noqa


SESSION_COOKIE_SECURE = True
SESSION_COOKIE_AGE = 60 * 10
SESSION_SAVE_EVERY_REQUEST = True

CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True

AWS_ACCESS_KEY_ID = env('AWS_STATIC_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = env('AWS_STATIC_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
AWS_QUERYSTRING_AUTH = env.bool('AWS_QUERYSTRING_AUTH')
AWS_S3_ENDPOINT_URL = env('AWS_S3_ENDPOINT_URL')

INSTALLED_APPS += [
    'raven.contrib.django.raven_compat',
    'storages',
]

DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

RAVEN_CONFIG = {
    'dsn': env('SENTRY_URL'),
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
    },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s '
                      '%(process)d %(thread)d %(message)s'
        },
    },
    'handlers': {
        'sentry': {
            'level': 'WARNING',
            'class': 'raven.contrib.django.raven_compat.handlers.SentryHandler',
            'tags': {'custom-tag': 'x'},
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
        },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
        },
    },
}
