# flake8: noqa
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('gate_block', '0006_auto_20141210_0905'),
    ]

    operations = [
        migrations.CreateModel(
            name='GateSubmission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('submitted', models.DateTimeField(default=datetime.datetime.now)),
                ('gate_user', models.ForeignKey(related_name=b'gate_user', to=settings.AUTH_USER_MODEL)),
                ('gateblock', models.ForeignKey(to='gate_block.GateBlock')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
