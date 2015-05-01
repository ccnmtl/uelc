# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pagetree', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Curveball',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.TextField(blank=True)),
                ('explanation', models.TextField(max_length=255, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CurveballBlock',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(blank=True)),
                ('curveball_one', models.ForeignKey(related_name='curveball_one', blank=True, to='curveball.Curveball', null=True)),
                ('curveball_three', models.ForeignKey(related_name='curveball_three', blank=True, to='curveball.Curveball', null=True)),
                ('curveball_two', models.ForeignKey(related_name='curveball_two', blank=True, to='curveball.Curveball', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CurveballSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submitted', models.DateTimeField(default=datetime.datetime.now)),
                ('curveball_user', models.ForeignKey(related_name='curveball_user', to=settings.AUTH_USER_MODEL)),
                ('curveballblock', models.ForeignKey(to='curveball.CurveballBlock')),
                ('section', models.ForeignKey(to='pagetree.Section')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
