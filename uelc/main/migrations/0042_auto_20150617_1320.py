# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0041_casequestion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='casequestion',
            name='quiz',
        ),
        migrations.DeleteModel(
            name='CaseQuestion',
        ),
    ]
