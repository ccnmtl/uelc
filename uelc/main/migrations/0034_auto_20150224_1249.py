# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0033_auto_20150224_1227'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='cohort',
            field=models.ManyToManyField(related_name='case_cohort', to='main.Cohort', blank=True),
            preserve_default=True,
        ),
    ]
