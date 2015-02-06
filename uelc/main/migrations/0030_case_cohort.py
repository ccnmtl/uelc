# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0029_auto_20150205_1930'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='cohort',
            field=models.ManyToManyField(default=1, related_name='case_cohort', to='main.Cohort', blank=True),
            preserve_default=True,
        ),
    ]
