# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0025_libraryitem_show'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='libraryitem',
            name='show',
        ),
    ]
