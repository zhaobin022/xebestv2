# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0019_auto_20160127_1512'),
    ]

    operations = [
        migrations.CreateModel(
            name='OsUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('username', models.CharField(unique=True, max_length=30)),
                ('server_group', models.ManyToManyField(to='cmdb.ServerGroup')),
            ],
        ),
    ]
