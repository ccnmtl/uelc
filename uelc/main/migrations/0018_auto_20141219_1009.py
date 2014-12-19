# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_textblockdt'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pageblockdt',
            name='after_decision',
        ),
        migrations.RemoveField(
            model_name='pageblockdt',
            name='choice',
        ),
        migrations.RemoveField(
            model_name='pageblockdt',
            name='pageblock_ptr',
        ),
        migrations.DeleteModel(
            name='PageBlockDT',
        ),
    ]
