# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_libraryitem'),
    ]

    operations = [
        migrations.AddField(
            model_name='libraryitem',
            name='name',
            field=models.TextField(default='test'),
            preserve_default=False,
        ),
    ]
