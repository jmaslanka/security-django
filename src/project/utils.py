from enum import Enum, EnumMeta
import logging
import requests

from django.conf import settings
from django.utils.translation import gettext_lazy as _

from ipware import get_client_ip


logger = logging.getLogger(__name__)


class ChoiceEnumMeta(EnumMeta):
    def __iter__(self):
        return ((tag, tag.value) for tag in super().__iter__())


class ChoiceEnum(Enum, metaclass=ChoiceEnumMeta):
    '''
    Author: https://github.com/treyhunner
    Usage:

        class Gender(ChoiceEnum):
            male = 'male'
            female = 'female'
            no_answer = 'no-answer'

        models.CharField(max_length=10, choices=Gender)
    '''
    pass


def is_valid_recaptcha(request) -> bool:
    '''
    Checking recaptcha response with Google servers.
    '''
    if not request:
        return False

    recaptcha_response = request.POST.get('g-recaptcha-response', False)

    if not recaptcha_response:
        return False

    url = 'https://www.google.com/recaptcha/api/siteverify'
    data = {
        'secret': settings.RECAPTCHA_PRIVATE_KEY,
        'response': recaptcha_response,
    }

    client_ip, is_routable = get_client_ip(request)
    if client_ip and is_routable:
        data['remoteip'] = client_ip

    try:
        response = requests.post(url, data=data, timeout=2)
        response.raise_for_status()
        result = response.json()
    except requests.RequestException as err:
        logger.error(err)
        # Since request failed we don't want our site to be blocked
        return True

    if result['success']:
        return True

    errors_to_log = ['missing-input-secret', 'invalid-input-secret']
    if 'error-codes' in result and result['error-codes'] in errors_to_log:
        logger.error(_('Invalid reCAPTCHA secret.'))

    return False
