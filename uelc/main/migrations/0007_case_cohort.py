# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_remove_case_cohort'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='cohort',
            field=models.ForeignKey(related_name=b'cohort', default=1, blank=True, to='main.Cohort'),
            preserve_default=True,
        ),
    ]
