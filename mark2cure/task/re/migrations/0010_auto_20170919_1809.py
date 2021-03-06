# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-09-20 01:09
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('relation', '0009_auto_20160523_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='conceptdocumentrelationship',
            name='stype',
            field=models.CharField(choices=[('d', 'Disease'), ('g', 'Gene'), ('c', 'Chemical')], default='d', max_length=1),
        ),
        migrations.AlterField(
            model_name='relationannotation',
            name='relation',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='annotations', to='relation.Relation'),
        ),
    ]
