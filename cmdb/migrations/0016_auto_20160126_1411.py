# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0015_auto_20160126_1408'),
    ]

    operations = [
        migrations.CreateModel(
            name='ServerGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group_name', models.CharField(unique=True, max_length=30)),
                ('description', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='server',
            name='server_group',
            field=models.ForeignKey(blank=True, to='cmdb.ServerGroup', null=True),
        ),
    ]
