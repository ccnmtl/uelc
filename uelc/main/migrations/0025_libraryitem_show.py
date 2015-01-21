# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_libraryitem_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='libraryitem',
            name='show',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
