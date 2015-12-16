# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20141126_1425'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case',
            name='cohort',
        ),
    ]
