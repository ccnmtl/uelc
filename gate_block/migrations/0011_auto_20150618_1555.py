# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gate_block', '0010_sectionsubmission'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gatesubmission',
            name='submitted',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=True,
        ),
    ]
