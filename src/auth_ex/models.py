import uuid

from django.contrib.auth.base_user import (
    AbstractBaseUser,
    BaseUserManager,
)
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _


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

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def set_password(self, raw_password):
        '''
        Increasing salt length from ~71 to ~130 bits.
        '''
        self.password = make_password(raw_password, get_random_string(22))
        self._password = raw_password
