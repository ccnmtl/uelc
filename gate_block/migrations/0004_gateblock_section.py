# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pagetree', '0001_initial'),
        ('gate_block', '0003_auto_20141202_1528'),
    ]

    operations = [
        migrations.AddField(
            model_name='gateblock',
            name='section',
            field=models.ForeignKey(default=1, to='pagetree.Section'),
            preserve_default=False,
        ),
    ]
