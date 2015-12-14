# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pagetree', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Case',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Cohort',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('user', models.ManyToManyField(to=settings.AUTH_USER_MODEL, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='case',
            name='cohort',
            field=models.ManyToManyField(related_name=b'cohort', to='main.Cohort', blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='case',
            name='hierarchy',
            field=models.ForeignKey(default=1, to='pagetree.Hierarchy'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='cohort',
            field=models.ManyToManyField(db_constraint=b'user', to='main.Cohort', blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='user',
            field=models.ForeignKey(related_name=b'profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
