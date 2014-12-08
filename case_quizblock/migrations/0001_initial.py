# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizblock', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseQuestion',
            fields=[
                ('question_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='quizblock.Question')),
            ],
            options={
            },
            bases=('quizblock.question',),
        ),
        migrations.CreateModel(
            name='CaseQuiz',
            fields=[
                ('quiz_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='quizblock.Quiz')),
            ],
            options={
            },
            bases=('quizblock.quiz',),
        ),
    ]
