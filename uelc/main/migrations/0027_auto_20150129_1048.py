# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_remove_libraryitem_show'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='profile_type',
            field=models.CharField(max_length=12, choices=[(None, b'--------'), (b'admin', b'Administrator'), (b'assistant', b'Assistant'), (b'group_user', b'Group User')]),
            preserve_default=True,
        ),
    ]
