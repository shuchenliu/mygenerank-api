# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-08-02 23:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0020_auto_20170628_2250'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskreductor',
            name='description',
            field=models.CharField(blank=True, max_length=800),
        ),
    ]