from hashlib import sha1
import requests
import logging

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.views.decorators.debug import sensitive_variables

from zxcvbn import zxcvbn


logger = logging.getLogger(__name__)


class ComplexityValidator:
    '''
    Validate password using zxcvbn password strength estimator.
    Password must have at least score of 3 (good).
    '''

    @sensitive_variables('password', 'result')
    def validate(self, password, user=None):
        result = zxcvbn(password)

        if result['score'] < 4:
            raise ValidationError(_(
                'Password is too weak. Please use stronger password.'
            ))

    def get_help_text(self):
        return _('Password cannot be too weak.')


class HaveIBeenPwnedValidator:
    '''
    Validate whether the password is found in HaveIBeenPwned DB.
    Source: https://haveibeenpwned.com/API/v2
    '''
    URL = 'https://api.pwnedpasswords.com/range/{hash_prefix}'

    @sensitive_variables('password', 'password_hash')
    def validate(self, password, user=None):
        password_hash = sha1(password.encode('utf-8')).hexdigest()
        password_prefix = password_hash[:5]

        try:
            response = requests.get(
                url=self.URL.format(hash_prefix=password_prefix),
                headers={'user-agent': 'Registration-Checker'},
            )
        except requests.RequestException:
            logger.exception('Error during checking leaked passwords.')
            return

        hashes_list = map(
            lambda suffix: password_prefix + suffix.split(':')[0],
            response.content.decode('utf-8').split('\r\n')
        )

        if password_hash in hashes_list:
            raise ValidationError(_(
                'Your password was found on leaked passwords list. '
                'Use different password and change it '
                'on sites where you are using it.'
            ))

    def get_help_text(self):
        return _('Password must not be previously leaked.')
