# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0042_sectionsubmission'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sectionsubmission',
            name='section',
        ),
        migrations.RemoveField(
            model_name='sectionsubmission',
            name='user',
        ),
        migrations.DeleteModel(
            name='SectionSubmission',
        ),
    ]
