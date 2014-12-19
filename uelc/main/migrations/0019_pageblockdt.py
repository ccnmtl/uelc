# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pagetree', '0001_initial'),
        ('main', '0018_auto_20141219_1009'),
    ]

    operations = [
        migrations.CreateModel(
            name='PageBlockDT',
            fields=[
                ('pageblock_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pagetree.PageBlock')),
                ('after_decision', models.ForeignKey(to='main.Decision')),
                ('choice', models.ForeignKey(to='main.Choice')),
            ],
            options={
            },
            bases=('pagetree.pageblock',),
        ),
    ]
