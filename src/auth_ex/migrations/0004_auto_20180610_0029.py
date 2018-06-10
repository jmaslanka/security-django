# Generated by Django 2.1a1 on 2018-06-10 00:29

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auth_ex', '0003_userotp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='type',
            field=models.CharField(choices=[('login', 'Login'), ('invalid_login', 'Invalid login'), ('password_change', 'Password change'), ('forgot_pass_request', 'Forgot password request'), ('forgot_pass_done', 'Forgot password done'), ('added_MFA', 'Added MFA'), ('removed_MFA', 'Removed MFA'), ('new_codes_MFA', 'New MFA recovery codes'), ('recovery_MFA', 'MFA with recovery code')], max_length=20, verbose_name='type'),
        ),
        migrations.AlterField(
            model_name='userotp',
            name='recovery_codes',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=10), blank=True, size=5),
        ),
    ]