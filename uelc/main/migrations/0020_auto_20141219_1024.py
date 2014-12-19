# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0019_pageblockdt'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pageblockdt',
            name='after_decision',
            field=models.CharField(max_length=2, blank=True),
        ),
        migrations.DeleteModel(
            name='Decision',
        ),
        migrations.AlterField(
            model_name='pageblockdt',
            name='choice',
            field=models.CharField(max_length=2, blank=True),
        ),
        migrations.DeleteModel(
            name='Choice',
        ),
    ]
