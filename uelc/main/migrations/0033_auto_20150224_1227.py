# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0032_caseanswer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='caseanswer',
            name='title',
            field=models.TextField(blank=True),
            preserve_default=True,
        ),
    ]
