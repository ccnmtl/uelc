# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case_quizblock', '0003_auto_20150130_1102'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='caseanswer',
            name='answer_ptr',
        ),
        migrations.RemoveField(
            model_name='caseanswer',
            name='case_question',
        ),
        migrations.DeleteModel(
            name='CaseAnswer',
        ),
        migrations.RemoveField(
            model_name='casequestion',
            name='case_quiz',
        ),
        migrations.RemoveField(
            model_name='casequestion',
            name='question_ptr',
        ),
        migrations.DeleteModel(
            name='CaseQuestion',
        ),
        migrations.RemoveField(
            model_name='casequiz',
            name='quiz_ptr',
        ),
        migrations.DeleteModel(
            name='CaseQuiz',
        ),
    ]
