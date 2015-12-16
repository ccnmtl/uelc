# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gate_block', '0002_submission'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='user_gate',
        ),
        migrations.AddField(
            model_name='submission',
            name='gate_user',
            field=models.ForeignKey(related_name=b'gate_user', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
