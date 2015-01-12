# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20150106_1420'),
    ]

    operations = [
        migrations.AddField(
            model_name='textblockdt',
            name='embed',
            field=models.TextField(default=0, blank=True),
            preserve_default=True,
        ),
    ]
