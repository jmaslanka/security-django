import uuid

from django.conf import settings
from django.contrib.auth.base_user import (
    AbstractBaseUser,
    BaseUserManager,
)
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _

from model_utils import Choices


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields['is_staff'] = True
        extra_fields['is_superuser'] = True
        extra_fields['is_active'] = True
        extra_fields.setdefault('first_name', 'Admin')
        extra_fields.setdefault('last_name', '-----')
        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    email = models.EmailField(
        _('email address'),
        unique=True,
    )
    first_name = models.CharField(
        _('first name'),
        max_length=30,
    )
    last_name = models.CharField(
        _('last name'),
        max_length=150,
    )

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active.'
        ),
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        auto_now_add=True,
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    EMAIL_FIELD = 'email'

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def set_password(self, raw_password):
        '''
        Increasing salt length from ~71 to ~130 bits.
        '''
        self.password = make_password(raw_password, get_random_string(22))
        self._password = raw_password

    def has_mfa_enabled(self):
        return hasattr(self, 'otp')


class Log(models.Model):
    '''
    Model to log important user actions.
    '''

    TYPES = Choices(
        ('login', _('Login')),
        ('invalid_login', _('Invalid login')),
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
