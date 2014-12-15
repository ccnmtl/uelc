# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20141211_1220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='casemap',
            name='value',
            field=models.TextField(blank=True),
        ),
    ]
