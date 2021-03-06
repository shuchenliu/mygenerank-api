# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2017-05-16 20:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0015_remove_riskreductoroption_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='riskreductoroption',
            name='created_on',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='riskreductor',
            name='condition',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reductors', to='api.Condition'),
        ),
    ]
