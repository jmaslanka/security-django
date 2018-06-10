import uuid

from django.conf import settings
from django.db import models
from django.db.models.functions import Now
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from model_utils import Choices


class Safe(models.Model):
    '''
    Model representing user's safe that contain all secrets.
    '''

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name=_('owner'),
        related_name='safes',
    )
    name = models.CharField(
        _('name'),
        max_length=30,
        default='Safe',
        blank=True,
    )
    description = models.CharField(
        _('description'),
        max_length=255,
        blank=True,
    )
    date_created = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
    )
    last_accessed = models.DateTimeField(
        _('last accessed'),
        default=timezone.now,
        blank=True,
    )

    def update_last_access_time(self):
        self.__class__.objects.filter(id=self.id).update(last_accessed=Now())


class SafeItem(models.Model):
    '''
    Model representing single item in safe.
    '''

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    safe = models.ForeignKey(
        Safe,
        on_delete=models.CASCADE,
        verbose_name=_('safe'),
        related_name='items',
    )
    notes = models.TextField(
        _('notes'),
        max_length=5000,
        blank=True,
    )


class ItemField(models.Model):
    '''
    Model representing single field in safe item.
    '''

    TYPES = Choices(
        ('text', _('Text')),
        ('password', _('Password')),
        ('date', _('Date')),
        ('email', _('Email')),
        ('url', _('URL')),
        ('otp', _('One-Time Password')),
    )

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )
    item = models.ForeignKey(
        SafeItem,
        on_delete=models.CASCADE,
        verbose_name=_('safe item'),
        related_name='fields',
    )
    type = models.CharField(
        _('type'),
        max_length=24,
        choices=TYPES,
    )
    name = models.CharField(
        _('name'),
        max_length=30,
        blank=True,
    )
    value = models.CharField(
        _('value'),
        max_length=255,
    )
