# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pageblocks', '0001_initial'),
        ('main', '0019_auto_20150106_1406'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextBlockDT',
            fields=[
                ('textblock_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pageblocks.TextBlock')),
                ('after_decision', models.CharField(default=0, max_length=2, blank=True)),
                ('choice', models.CharField(default=0, max_length=2, blank=True)),
            ],
            options={
            },
            bases=('pageblocks.textblock',),
        ),
        migrations.RemoveField(
            model_name='textblockwysiwyg',
            name='htmlblockwysiwyg_ptr',
        ),
        migrations.DeleteModel(
            name='TextBlockWYSIWYG',
        ),
    ]
