# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curveball', '0003_auto_20150529_1530'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='curveballsubmission',
            name='section',
        ),
        migrations.AlterField(
            model_name='curveballsubmission',
            name='submitted',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
