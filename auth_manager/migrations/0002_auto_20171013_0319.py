# -*- coding: utf-8 -*-
# Generated by Django 1.11.6 on 2017-10-13 03:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofilemodel',
            options={'verbose_name': 'user profile', 'verbose_name_plural': 'user profiles'},
        ),
    ]
