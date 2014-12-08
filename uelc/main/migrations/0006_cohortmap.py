# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20141126_1425'),
    ]

    operations = [
        migrations.CreateModel(
            name='CohortMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('choice_val', models.DecimalField(default=0.0, max_digits=6, decimal_places=2)),
                ('cohort', models.ForeignKey(to='main.Cohort')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
