# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizblock', '__first__'),
        ('main', '0031_imageuploaditem'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=255, blank=True)),
                ('description', models.TextField(blank=True)),
                ('answer', models.ForeignKey(to='quizblock.Answer')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
