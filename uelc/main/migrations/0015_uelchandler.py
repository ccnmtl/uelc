# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pagetree', '0001_initial'),
        ('main', '0014_auto_20141215_1426'),
    ]

    operations = [
        migrations.CreateModel(
            name='UELCHandler',
            fields=[
                ('section_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='pagetree.Section')),
            ],
            options={
                'abstract': False,
            },
            bases=('pagetree.section',),
        ),
    ]
