# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_remove_userprofile_cohort'),
    ]

    operations = [
        migrations.AlterField(
            model_name='case',
            name='hierarchy',
            field=models.ForeignKey(to='pagetree.Hierarchy'),
        ),
    ]
