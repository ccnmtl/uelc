# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0007_case_cohort'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseMap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value', models.DecimalField(max_digits=6, decimal_places=2)),
                ('case', models.ForeignKey(to='main.Case')),
                ('user', models.ManyToManyField(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
