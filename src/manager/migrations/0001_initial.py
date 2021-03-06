# Generated by Django 2.2.5 on 2019-09-16 12:01

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import config.utils
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Safe',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('image', models.ImageField(blank=True, upload_to=config.utils.upload_to_classname_uuid, verbose_name='image')),
                ('data', models.TextField(blank=True, verbose_name='encrypted data')),
                ('date_created', models.DateTimeField(auto_now_add=True, verbose_name='created at')),
                ('last_accessed', models.DateTimeField(blank=True, default=django.utils.timezone.now, verbose_name='last accessed')),
            ],
            options={
                'verbose_name': 'Safe',
                'verbose_name_plural': 'Safes',
            },
        ),
        migrations.CreateModel(
            name='SafeItem',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('data', models.TextField(blank=True, verbose_name='encrypted data')),
                ('safe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='manager.Safe', verbose_name='safe')),
            ],
            options={
                'verbose_name': 'Safe item',
                'verbose_name_plural': 'Safe items',
            },
        ),
    ]
