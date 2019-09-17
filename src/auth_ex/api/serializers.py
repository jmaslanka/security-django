from django.contrib.auth import authenticate
from django.utils.translation import gettext as _
from rest_framework import serializers

from auth_ex.utils import is_valid_mfa_code, validate_device_cookie
from config.utils import is_valid_recaptcha


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=200)
    password = serializers.CharField(write_only=True)
    code = serializers.RegexField(
        regex=r'^[0-9]{6}$|^[a-zA-Z0-9]{10}$',
        min_length=6, max_length=10,
        allow_blank=True, required=False,
    )

    error_messages = {
        'invalid_login': _(
            'Login failed. Note that fields may be case-sensitive.'
        ),
        'invalid_recaptcha': _('Invalid reCAPTCHA response.'),
        'throttled_login': _(
            'There were too many unsuccessful login attempts, please try '
            'again later.'
        ),
        'invalid_mfa': _(
            'Invalid one-time password code.'
        )
    }

    def get_invalid_captcha_error(self):
        return serializers.ValidationError(
            self.error_messages['invalid_recaptcha'],
            code='invalid_recaptcha',
        )

    def get_throttled_login_error(self):
        return serializers.ValidationError(
            self.error_messages['throttled_login'],
            code='throttled_login',
        )

    def get_invalid_mfa_error(self):
        return serializers.ValidationError(
            self.error_messages['invalid_mfa'],
            code='invalid_mfa',
        )

    def get_invalid_login_error(self):
        return serializers.ValidationError(
            self.error_messages['invalid_login'],
            code='invalid_login',
        )

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        code = attrs.get('code')

        if username and password:
            if not validate_device_cookie(self.request, username):
                raise self.get_throttled_login_error()

            if not is_valid_recaptcha(self.request):
                raise self.get_invalid_captcha_error()

            self.user = authenticate(
                self.request, username=username, password=password)

            if self.user is None or not self.user.is_active:
                raise self.get_invalid_login_error()
            else:
                if not is_valid_mfa_code(self.user, code):
                    raise self.get_invalid_mfa_error()

        return attrs
