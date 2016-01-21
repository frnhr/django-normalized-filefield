# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-21 01:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='MyModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=254)),
                ('ac_required_file', models.FileField(upload_to='media/uploads/required')),
                ('ac_optional_file', models.FileField(blank=True, null=True, upload_to='media/uploads/optional')),
            ],
        ),
    ]