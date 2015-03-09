# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0035_auto_20150227_1410'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='textblockdt',
            name='after_decision',
        ),
    ]
