# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-12-01 06:21
from __future__ import unicode_literals

import blog.models
import django.core.files.storage
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0011_post_authors'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='cover_image',
            field=models.ImageField(default='DonutsDonut.png', storage=django.core.files.storage.FileSystemStorage(base_url='/media/uploads/', location='C:\\Users\\pedro\\OneDrive\\Documents\\Heroku\\DonutProject\\DonutProject\\config\\mediafiles/uploads/'), upload_to=blog.models.image_directory_path),
        ),
    ]
