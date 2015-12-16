# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0034_auto_20150224_1249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='cohort',
            field=models.ForeignKey(related_name='user_profile_cohort', to='main.Cohort'),
            preserve_default=True,
        ),
    ]
