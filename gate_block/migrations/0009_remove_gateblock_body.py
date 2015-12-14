# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gate_block', '0008_gatesubmission_section'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gateblock',
            name='body',
        ),
    ]
