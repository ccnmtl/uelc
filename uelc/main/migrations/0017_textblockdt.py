# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pageblocks', '0001_initial'),
        ('main', '0016_choice_decision_pageblockdt'),
    ]

    operations = [
        migrations.CreateModel(
            name='TextBlockDT',
            fields=[
                ('textblock_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pageblocks.TextBlock')),
            ],
            options={
            },
            bases=('pageblocks.textblock',),
        ),
    ]
