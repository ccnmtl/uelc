# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0038_auto_20150312_0950'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_type',
            field=models.CharField(max_length=12, choices=[(b'admin', b'Administrator'), (b'assistant', b'Assistant'), (b'group_user', b'Group User')]),
            preserve_default=True,
        ),
    ]
