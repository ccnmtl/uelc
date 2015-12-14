# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0011_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cohortmap',
            name='cohort',
        ),
        migrations.RemoveField(
            model_name='cohortmap',
            name='user',
        ),
        migrations.DeleteModel(
            name='CohortMap',
        ),
        migrations.RemoveField(
            model_name='case',
            name='user',
        ),
    ]
