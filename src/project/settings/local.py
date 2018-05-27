from .default import *  # noqa

AUTH_PASSWORD_VALIDATORS = list()
TEMPLATES[0]['OPTIONS']['context_processors'] += [
    'django.template.context_processors.debug',
]

RECAPTCHA_DISABLE = True
