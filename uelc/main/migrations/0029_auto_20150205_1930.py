# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_merge'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='case',
            name='cohort',
        ),
        migrations.RemoveField(
            model_name='cohort',
            name='user',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='cohort',
            field=models.ForeignKey(related_name='user_profile_cohort', default=1, to='main.Cohort'),
            preserve_default=True,
        ),
    ]
