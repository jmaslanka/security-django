import re
import string
import requests

from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class ComplexityValidator:
    '''
    Validate whether the password has at least one of given characters:
    - digit
    - lower case
    - upper case
    - special
    '''
    VALIDATORS = [
        re.compile('\d'),  # digits
        re.compile('[a-z]'),  # lowercase
        re.compile('[A-Z]'),  # uppercase
        re.compile(f'[{re.escape(string.punctuation)}]'),  # special
    ]

    def validate(self, password, user=None):
        checks = 0
        for validator in self.VALIDATORS:
            checks += 1 if validator.search(password) else 0

        if checks < 3:
            raise ValidationError(self.get_help_text())

    def get_help_text(self):
        return _(
            'Password must contain 3 out of 4 characters: '
            'lowercase, uppercase, digit, special.'
        )


class HaveIBeenPwnedValidator:
    '''
    Validate whether the password is found in HaveIBeenPwned DB.
    Source: https://haveibeenpwned.com/API/v2
    '''
    URL = 'https://api.pwnedpasswords.com/pwnedpassword/{password}'

    def validate(self, password, user=None):
        response = requests.get(
            url=self.URL.format(password=password),
            headers={'user-agent': 'Registration-Checker'},
        )
        if response.status_code == 200:
            raise ValidationError(_(
                'Your password was found on hacked passwords list. '
                'Use different password and change it '
                'on sites where you are using it.'
            ))

    def get_help_text(self):
        return _('Password must not be on hacked passwords list.')
