# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0039_auto_20150323_1524'),
    ]

    operations = [
        migrations.AddField(
            model_name='case',
            name='description',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
