import logging
import requests

from django.conf import settings
from django.contrib.auth.hashers import Argon2PasswordHasher
from django.contrib.gis.geoip2 import GeoIP2
from django.utils.translation import gettext_lazy as _

from ipware import get_client_ip
from user_agents import parse as parse_ua


logger = logging.getLogger(__name__)


class Argon2PasswordHasher(Argon2PasswordHasher):
    time_cost = 10  # Default 2
    memory_cost = 4096  # Default 512
    parallelism = 2

    def encode(self, password, salt):
        argon2 = self._load_library()
        data = argon2.low_level.hash_secret(
            password.encode(),
            salt.encode(),
            time_cost=self.time_cost,
            memory_cost=self.memory_cost,
            parallelism=self.parallelism,
            hash_len=40,  # Default 16
            type=argon2.low_level.Type.I,
        )

        return self.algorithm + data.decode('ascii')


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


def get_client_details(request) -> dict:
    '''
    Given valid request returns user's ip, location and user-agent.
    '''
    if not request:
        return dict()

    client_ip, is_routable = get_client_ip(request)
    client_ip = client_ip if client_ip and is_routable else None
    location = ''

    if client_ip:
        result = GeoIP2().city(client_ip)
        location = '{city}, {country}'.format(
            country=result.get('country_name', ''),
            city=result.get('city', ''),
        )

    user_agent = request.META.get('HTTP_USER_AGENT', '')

    if user_agent:
        user_agent = str(parse_ua(user_agent))

    return {
        'ip': client_ip,
        'location': location,
        'user_agent': user_agent,
    }
