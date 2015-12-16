# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20141208_1107'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casemap',
            name='value',
            field=models.DecimalField(max_digits=6, decimal_places=2, blank=True),
        ),
    ]
