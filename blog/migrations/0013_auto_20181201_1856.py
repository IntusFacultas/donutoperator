# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-01 23:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0012_auto_20181201_0121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='cover_image',
            field=models.ImageField(default='DonutsDonut.png', upload_to=''),
        ),
    ]
