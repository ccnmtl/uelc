# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2016-12-09 21:42
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0045_auto_20161130_1605'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='libraryitem',
            name='case',
        ),
        migrations.RemoveField(
            model_name='libraryitem',
            name='user',
        ),
        migrations.DeleteModel(
            name='LibraryItem',
        ),
    ]