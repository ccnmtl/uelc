# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizblock', '__first__'),
        ('main', '0040_case_description'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseQuestion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question_type', models.CharField(max_length=256, choices=[(b'single choice', b'Multiple Choice: Single answer')])),
                ('explanation', models.TextField(blank=True)),
                ('intro_text', models.TextField(blank=True)),
                ('quiz', models.ForeignKey(to='quizblock.Quiz')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
