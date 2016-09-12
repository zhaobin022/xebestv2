# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0025_auto_20160216_1436'),
    ]

    operations = [
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('age', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ['name'],
                'abstract': False,
                'db_table': 'student_info',
            },
        ),
    ]
