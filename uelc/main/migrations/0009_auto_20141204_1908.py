# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_casecohortuser'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='casecohortuser',
            name='case',
        ),
        migrations.RemoveField(
            model_name='casecohortuser',
            name='cohort',
        ),
        migrations.RemoveField(
            model_name='casecohortuser',
            name='user',
        ),
        migrations.DeleteModel(
            name='CaseCohortUser',
        ),
    ]
