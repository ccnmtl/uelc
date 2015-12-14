# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gate_block', '0005_remove_gateblock_section'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submission',
            name='gate_user',
        ),
        migrations.RemoveField(
            model_name='submission',
            name='gateblock',
        ),
        migrations.DeleteModel(
            name='Submission',
        ),
    ]
