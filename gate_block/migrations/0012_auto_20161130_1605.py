# flake8: noqa
# -*- coding: utf-8 -*-
# Generated by Django 1.9.10 on 2016-11-30 21:05
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gate_block', '0011_auto_20150618_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sectionsubmission',
            name='section',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='section_submitted', to='pagetree.Section'),
        ),
    ]
