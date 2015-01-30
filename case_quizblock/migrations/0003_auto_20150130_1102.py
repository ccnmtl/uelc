# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quizblock', '__first__'),
        ('case_quizblock', '0002_auto_20150130_1058'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='caseanswer',
            name='id',
        ),
        migrations.RemoveField(
            model_name='caseanswer',
            name='question',
        ),
        migrations.AddField(
            model_name='caseanswer',
            name='answer_ptr',
            field=models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, default=1, serialize=False, to='quizblock.Answer'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='caseanswer',
            name='case_question',
            field=models.ForeignKey(default=1, to='case_quizblock.CaseQuestion'),
            preserve_default=True,
        ),
    ]
