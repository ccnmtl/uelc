# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0037_auto_20150311_1001'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='cohort',
            field=models.ForeignKey(related_name='user_profile_cohort', blank=True, to='main.Cohort', null=True),
            preserve_default=True,
        ),
    ]
