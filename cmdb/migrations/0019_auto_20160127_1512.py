# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cmdb', '0018_auto_20160127_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='app',
            name='task',
            field=models.ForeignKey(blank=True, to='cmdb.TaskLog', null=True),
        ),
        migrations.AlterField(
            model_name='server',
            name='new_password',
            field=models.CharField(max_length=40, null=True, blank=True),
        ),
    ]
