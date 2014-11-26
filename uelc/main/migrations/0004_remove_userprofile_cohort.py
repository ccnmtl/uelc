# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20141126_1253'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='cohort',
        ),
    ]
