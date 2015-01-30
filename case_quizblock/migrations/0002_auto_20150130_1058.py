# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('case_quizblock', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CaseAnswer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('question', models.ForeignKey(to='case_quizblock.CaseQuestion')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='casequestion',
            name='case_quiz',
            field=models.ForeignKey(default=3, to='case_quizblock.CaseQuiz'),
            preserve_default=True,
        ),
    ]
