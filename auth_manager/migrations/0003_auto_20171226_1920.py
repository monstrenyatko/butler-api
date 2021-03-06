# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-12-26 19:20
from __future__ import unicode_literals

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import auth_manager.models


def populateMqttAclTemplateModel(apps, schema_editor):
    MqttAclTemplateModel = apps.get_model("auth_manager", "MqttAclTemplateModel")
    template = MqttAclTemplateModel(name='USER_DEFAULT', template='/butler/%u/')
    template.save()


def populateMqttAclModel(apps, schema_editor):
    MqttAclTemplateModel = apps.get_model("auth_manager", "MqttAclTemplateModel")
    acl_template = MqttAclTemplateModel.objects.get(name='USER_DEFAULT')
    MqttAclModel = apps.get_model("auth_manager", "MqttAclModel")
    UserModel = apps.get_model(settings.AUTH_USER_MODEL)
    for user in UserModel.objects.all():
        acl_topic = auth_manager.models.mqtt_acl_template_to_topic(acl_template.template, user)
        acl = MqttAclModel(
            user=user,
            topic=acl_topic,
            access=3,
        )
        acl.save()


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth_manager', '0002_auto_20171013_0319'),
    ]

    operations = [
        migrations.CreateModel(
            name='MqttAclModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('topic', models.CharField(max_length=150, validators=[django.core.validators.RegexValidator('^([0-9a-zA-Z\\-_\\/])*$', 'Only Alphanumeric characters, Hyphen, Underscore, Forward-Slash symbols are allowed')])),
                ('access', models.PositiveSmallIntegerField(choices=[(1, 'READ'), (2, 'WRITE'), (3, 'READ+WRITE')])),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='mqtt_acl', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'mqtt acl',
                'verbose_name_plural': 'mqtt acl',
                'db_table': 'mqtt_acl',
            },
        ),
        migrations.CreateModel(
            name='MqttAclTemplateModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(choices=[('USER_DEFAULT', 'USER DEFAULT')], max_length=50, unique=True, validators=[django.core.validators.RegexValidator('^[0-9a-zA-Z\\-_]*$', 'Only Alphanumeric characters, Hyphen and Underscore symbols are allowed')])),
                ('template', models.CharField(max_length=150, unique=True, validators=[django.core.validators.RegexValidator('^([0-9a-zA-Z\\-_\\/]|(%u))*$', 'Only Alphanumeric characters, Hyphen, Underscore, Forward-Slash symbols are allowed plus template arguments like: %u - user-name')])),
            ],
            options={
                'verbose_name': 'mqtt acl template',
                'verbose_name_plural': 'mqtt acl templates',
                'db_table': 'mqtt_acl_template',
            },
        ),
        migrations.RunPython(
            populateMqttAclTemplateModel
        ),
        migrations.RunPython(
            populateMqttAclModel
        ),
    ]
