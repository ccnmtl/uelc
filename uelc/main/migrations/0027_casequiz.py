# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizblock', '__first__'),
        ('main', '0026_remove_libraryitem_show'),
    ]

    operations = [
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
