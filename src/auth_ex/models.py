from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from model_utils import Choices


class UserOTP(models.Model):
    '''
    Model to keep information on user's 2FA.
    '''

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='otp',
        verbose_name=_('user'),
        on_delete=models.CASCADE,
    )
    secret_key = models.CharField(
        _('secret_key'),
        max_length=32,
    )
    recovery_codes = ArrayField(
        models.CharField(max_length=10),
        size=5,
        blank=True,
    )
    created = models.DateTimeField(
        _('create'),
        auto_now_add=True,
    )

    class Meta:
        verbose_name = _('User OTP')
        verbose_name_plural = _('Users OTP')

    def __str__(self):
        return self.user_id


class Log(models.Model):
    '''
    Model to log important user actions.
    '''

    TYPES = Choices(
        ('login', _('Login')),
        ('invalid_login', _('Invalid login')),
        ('invalid_login_mfa', _('Invalid MFA code (login)')),
        ('password_change', _('Password change')),
        ('forgot_pass_request', _('Forgot password request')),
        ('forgot_pass_done', _('Forgot password done')),
        ('added_MFA', _('Added MFA')),
        ('removed_MFA', _('Removed MFA')),
        ('new_codes_MFA', _('New MFA recovery codes')),
        ('recovery_MFA', _('MFA with recovery code')),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('user'),
        related_name='logs',
        null=True,
        on_delete=models.SET_NULL,
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=TYPES,
    )
    date = models.DateTimeField(
        _('date'),
        auto_now_add=True,
    )
    keep = models.BooleanField(
        _('keep'),
        default=False,
    )
    ip = models.GenericIPAddressField(
        _('ip address'),
        blank=True,
        null=True,
    )
    user_agent = models.CharField(
        _('user agent'),
        max_length=255,
        blank=True,
    )
    location = models.CharField(
        _('location'),
        max_length=127,
        blank=True,
    )

    class Meta:
        verbose_name = _('log')
        verbose_name_plural = _('logs')

    def __str__(self):
        return f'{self.type} {self.user_id}'


class FailedAuthentication(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('user'),
        related_name='failed_authentications',
        on_delete=models.CASCADE,
    )
    date = models.DateTimeField(_('date'), auto_now_add=True)
    cookie = models.CharField(_('cookie'), max_length=200, null=True)

    class Meta:
        verbose_name = _('Failed authentication')
        verbose_name_plural = _('Failed authentications')
        indexes = [
            models.Index(fields=['user', 'cookie', '-date'])
        ]
