import uuid

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import (
    PermissionsMixin,
    UserManager,
)
from django.db import models
from django.utils.translation import gettext_lazy as _


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

    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)

    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_(
            'Designates whether this user should be treated as active. '
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

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()
