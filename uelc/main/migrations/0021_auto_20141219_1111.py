# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_auto_20141219_1024'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='pageblockdt',
            name='pageblock_ptr',
        ),
        migrations.DeleteModel(
            name='PageBlockDT',
        ),
        migrations.AddField(
            model_name='textblockdt',
            name='after_decision',
            field=models.CharField(default=0, max_length=2, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='textblockdt',
            name='choice',
            field=models.CharField(default=0, max_length=2, blank=True),
            preserve_default=True,
        ),
    ]
