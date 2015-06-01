# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('curveball', '0002_curveballsubmission_curveball'),
    ]

    operations = [
        migrations.RenameField(
            model_name='curveballsubmission',
            old_name='curveball_user',
            new_name='group_curveball',
        ),
        migrations.AddField(
            model_name='curveballsubmission',
            name='group_confirmation',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
