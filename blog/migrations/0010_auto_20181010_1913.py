# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2018-10-10 23:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0009_auto_20181010_1838'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='publish_date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Publish Date'),
        ),
        migrations.AlterField(
            model_name='post',
            name='created',
            field=models.DateTimeField(editable=False, verbose_name='Creation Date'),
        ),
    ]
