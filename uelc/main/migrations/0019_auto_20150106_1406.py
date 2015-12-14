# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pageblocks', '0001_initial'),
        ('main', '0018_auto_20150106_1305'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextBlockWYSIWYG',
            fields=[
                ('htmlblockwysiwyg_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pageblocks.HTMLBlockWYSIWYG')),
                ('after_decision', models.CharField(default=0, max_length=2, blank=True)),
                ('choice', models.CharField(default=0, max_length=2, blank=True)),
            ],
            options={
            },
            bases=('pageblocks.htmlblockwysiwyg',),
        ),
        migrations.RemoveField(
            model_name='textblockdt',
            name='textblock_ptr',
        ),
        migrations.DeleteModel(
            name='TextBlockDT',
        ),
    ]
