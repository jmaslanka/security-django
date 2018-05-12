from .default import *  # noqa


AUTH_PASSWORD_VALIDATORS = list()
TEMPLATES['OPTIONS']['context_processors'] += [
    'django.template.context_processors.debug',
]
