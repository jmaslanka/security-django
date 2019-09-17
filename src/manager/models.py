import uuid

from django.conf import settings
from django.db import models
from django.db.models.functions import Now
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from config.utils import upload_to_classname_uuid


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
    image = models.ImageField(
        _('image'),
        upload_to=upload_to_classname_uuid,
        blank=True,
    )
    data = models.TextField(
        _('encrypted data'),
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

    class Meta:
        verbose_name = _('Safe')
        verbose_name_plural = _('Safes')

    def __str__(self):
        return f'{self.id} (UserID: {self.owner_id})'

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
    data = models.TextField(
        _('encrypted data'),
        blank=True,
    )

    class Meta:
        verbose_name = _('Safe item')
        verbose_name_plural = _('Safe items')

    def __str__(self):
        return f'{self.id} (SafeID: {self.safe_id})'
